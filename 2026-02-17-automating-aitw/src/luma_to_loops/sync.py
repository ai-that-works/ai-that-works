#!/usr/bin/env python3
"""
Add Luma calendar contacts to a Loops mailing list.

The sync is strictly additive. For every email address on the Luma calendar it
asks Loops whether that contact already exists; if it does, the contact is left
completely untouched (no name, list membership, or subscription change). Only
addresses Loops has never seen are created.

Nothing is written unless --apply is passed.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, TextIO

import requests

from src.loops.constants import DEFAULT_CONTACT_SOURCE
from src.loops.loops_client import LoopsClient
from src.luma.luma_client import CalendarContact, LumaClient


def normalize_email(email: str) -> str:
    """
    Normalize an email address for comparison.

    Args:
        email: Raw email address

    Returns:
        Lowercased, whitespace-stripped address (empty string if unusable)
    """
    return (email or "").strip().lower()


@dataclass
class SyncResult:
    """Outcome of a Luma -> Loops sync run."""

    applied: bool
    mailing_list_ids: List[str]
    luma_contacts: int = 0
    unique_emails: int = 0
    skipped_no_email: int = 0
    duplicates_within_luma: int = 0
    already_in_loops: List[str] = field(default_factory=list)
    to_add: List[Dict[str, Optional[str]]] = field(default_factory=list)
    created: List[str] = field(default_factory=list)
    lookup_failed: List[Dict[str, str]] = field(default_factory=list)
    failed: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize the result for the JSON report."""
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "applied": self.applied,
            "mailing_list_ids": self.mailing_list_ids,
            "counts": {
                "luma_contacts": self.luma_contacts,
                "unique_emails": self.unique_emails,
                "skipped_no_email": self.skipped_no_email,
                "duplicates_within_luma": self.duplicates_within_luma,
                "already_in_loops": len(self.already_in_loops),
                "lookup_failed": len(self.lookup_failed),
                "to_add": len(self.to_add),
                "created": len(self.created),
                "failed": len(self.failed),
            },
            "already_in_loops": self.already_in_loops,
            "lookup_failed": self.lookup_failed,
            "to_add": self.to_add,
            "created": self.created,
            "failed": self.failed,
        }


def load_lookup_cache(cache_path: Optional[Path]) -> Dict[str, bool]:
    """
    Load previously recorded "is this email in Loops?" answers.

    A full run is thousands of lookups; checkpointing them means an
    interrupted run resumes instead of starting over.

    Args:
        cache_path: JSONL cache file, or None to skip caching

    Returns:
        Mapping of email -> whether Loops already has that contact
    """
    if cache_path is None or not cache_path.exists():
        return {}

    cache: Dict[str, bool] = {}
    for line in cache_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            cache[entry["email"]] = entry["exists"]
        except (json.JSONDecodeError, KeyError):
            continue  # ignore a truncated final line from a killed run

    return cache


def append_to_cache(handle: Optional[TextIO], email: str, exists: bool) -> None:
    """
    Record one lookup answer to the cache file immediately.

    Args:
        handle: Open cache file, or None if caching is disabled
        email: The address that was looked up
        exists: Whether Loops already had the contact
    """
    if handle is None:
        return
    handle.write(json.dumps({"email": email, "exists": exists}) + "\n")
    handle.flush()


def dedupe_luma_contacts(
    contacts: List[CalendarContact],
) -> tuple[Dict[str, CalendarContact], int, int]:
    """
    Collapse the Luma contact list to one entry per email address.

    Args:
        contacts: Contacts as returned by Luma

    Returns:
        (contacts keyed by normalized email, count without an email,
         count of within-Luma duplicates)
    """
    by_email: Dict[str, CalendarContact] = {}
    skipped_no_email = 0
    duplicates = 0

    for contact in contacts:
        email = normalize_email(contact.email)
        if not email or "@" not in email:
            skipped_no_email += 1
            continue
        if email in by_email:
            duplicates += 1
            # Keep whichever record carries a name.
            existing = by_email[email]
            if not existing.first_name and contact.first_name:
                by_email[email] = contact
            continue
        by_email[email] = contact

    return by_email, skipped_no_email, duplicates


def sync_luma_to_loops(
    mailing_list_ids: List[str],
    apply: bool = False,
    source: str = DEFAULT_CONTACT_SOURCE,
    max_contacts: Optional[int] = None,
    cache_path: Optional[Path] = None,
    verbose: bool = True,
) -> SyncResult:
    """
    Add Luma calendar contacts that Loops does not already have.

    Args:
        mailing_list_ids: Loops mailing lists to subscribe new contacts to
        apply: If False (default), report what would happen without writing
        source: Source label recorded on newly created Loops contacts
        max_contacts: Only consider the first N Luma contacts (for testing)
        cache_path: JSONL file checkpointing lookups so a run can resume
        verbose: Print progress to stdout

    Returns:
        SyncResult describing what was found and what was created
    """
    luma = LumaClient()
    loops = LoopsClient()

    result = SyncResult(applied=apply, mailing_list_ids=mailing_list_ids)

    if verbose:
        print("Fetching contacts from Luma...")
    contacts = luma.list_calendar_contacts(max_contacts=max_contacts)
    result.luma_contacts = len(contacts)

    by_email, skipped_no_email, duplicates = dedupe_luma_contacts(contacts)
    result.unique_emails = len(by_email)
    result.skipped_no_email = skipped_no_email
    result.duplicates_within_luma = duplicates

    if verbose:
        print(
            f"  {result.luma_contacts} Luma contacts -> {result.unique_emails} unique emails"
            f" ({duplicates} duplicate, {skipped_no_email} without an email)"
        )
        print("Checking each address against Loops...")

    cache = load_lookup_cache(cache_path)
    if verbose and cache:
        print(f"  resuming with {len(cache)} lookups already cached")

    cache_handle = open(cache_path, "a") if cache_path else None

    try:
        for index, (email, contact) in enumerate(sorted(by_email.items()), start=1):
            exists = cache.get(email)

            if exists is None:
                try:
                    exists = loops.contact_exists(email)
                except requests.RequestException as exc:
                    # One flaky address must not cost us the whole run.
                    result.lookup_failed.append({"email": email, "error": str(exc)})
                    continue
                append_to_cache(cache_handle, email, exists)

            if exists:
                result.already_in_loops.append(email)
            else:
                result.to_add.append(
                    {
                        "email": email,
                        "firstName": contact.first_name,
                        "lastName": contact.last_name,
                    }
                )

            if verbose and index % 100 == 0:
                print(f"  checked {index}/{result.unique_emails}")
    finally:
        if cache_handle:
            cache_handle.close()

    if verbose:
        print(
            f"  {len(result.already_in_loops)} already in Loops (untouched),"
            f" {len(result.to_add)} new,"
            f" {len(result.lookup_failed)} could not be checked"
        )

    if not apply:
        if verbose:
            print("\nDry run - nothing was written. Re-run with --apply to create them.")
        return result

    if verbose:
        print(f"\nCreating {len(result.to_add)} contacts in Loops...")

    cache_handle = open(cache_path, "a") if cache_path else None

    for index, entry in enumerate(result.to_add, start=1):
        try:
            loops.create_contact(
                email=entry["email"],
                first_name=entry["firstName"],
                last_name=entry["lastName"],
                mailing_list_ids=mailing_list_ids,
                source=source,
            )
            result.created.append(entry["email"])
            # Now that they exist, a resumed run should skip them.
            append_to_cache(cache_handle, entry["email"], True)
        except Exception as exc:  # noqa: BLE001 - report and keep going
            result.failed.append({"email": entry["email"], "error": str(exc)})

        if verbose and index % 100 == 0:
            print(f"  created {index}/{len(result.to_add)}")

    if cache_handle:
        cache_handle.close()

    if verbose:
        print(f"  {len(result.created)} created, {len(result.failed)} failed")

    return result


def print_mailing_lists() -> None:
    """Print the account's Loops mailing lists and their IDs."""
    for mailing_list in LoopsClient().list_mailing_lists():
        visibility = "public" if mailing_list.is_public else "private"
        print(f"{mailing_list.id}  {mailing_list.name} ({visibility})")


def main():
    parser = argparse.ArgumentParser(
        description="Add Luma calendar contacts to a Loops mailing list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list-mailing-lists
  %(prog)s --list-id cldc6f1jc00i7mm0fdgxq1xfs
  %(prog)s --list-id cldc6f1jc00i7mm0fdgxq1xfs --apply --output /tmp/luma_to_loops.json
        """,
    )

    parser.add_argument(
        "--list-mailing-lists",
        action="store_true",
        help="Print the Loops mailing lists with their IDs, then exit",
    )

    parser.add_argument(
        "--list-id",
        "-l",
        action="append",
        default=[],
        dest="list_ids",
        help="Loops mailing list ID to add new contacts to (repeatable)",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually create the contacts (default is a dry run)",
    )

    parser.add_argument(
        "--source",
        default=DEFAULT_CONTACT_SOURCE,
        help=f"Source label for new contacts (default: {DEFAULT_CONTACT_SOURCE})",
    )

    parser.add_argument(
        "--max-contacts",
        type=int,
        help="Only consider the first N Luma contacts (for testing)",
    )

    parser.add_argument(
        "--cache",
        type=Path,
        default=Path(".luma_to_loops_cache.jsonl"),
        help="JSONL file checkpointing Loops lookups so an interrupted run resumes "
        "(default: .luma_to_loops_cache.jsonl)",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Do not read or write the lookup checkpoint file",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Write a JSON report of the run to this path",
    )

    args = parser.parse_args()

    try:
        if args.list_mailing_lists:
            print_mailing_lists()
            return

        if not args.list_ids:
            parser.error(
                "--list-id is required (run --list-mailing-lists to find the ID)"
            )

        result = sync_luma_to_loops(
            mailing_list_ids=args.list_ids,
            apply=args.apply,
            source=args.source,
            max_contacts=args.max_contacts,
            cache_path=None if args.no_cache else args.cache,
        )

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result.to_dict(), indent=2))
            print(f"\nReport written to {args.output}")

        if result.failed or result.lookup_failed:
            sys.exit(1)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running sync: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
