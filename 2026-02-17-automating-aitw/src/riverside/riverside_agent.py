"""Riverside.fm browser automation agent for scheduling sessions."""

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from playwright.sync_api import sync_playwright, Page, Browser


@dataclass
class SessionDetails:
    """Details for a Riverside recording session."""

    name: str
    description: str
    date: datetime  # Date and start time
    duration_minutes: int = 60
    guests: Optional[List[str]] = None  # List of guest email addresses


class RiversideAgent:
    """Browser automation agent for Riverside.fm."""

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        headless: bool = False,
        screenshot_dir: Optional[str] = None
    ):
        """
        Initialize the Riverside agent.

        Args:
            email: Riverside login email. If not provided, reads from RIVERSIDE_LOGIN env var.
            password: Riverside password. If not provided, reads from RIVERSIDE_PASSWORD env var.
            headless: Whether to run browser in headless mode (default: False for debugging).
            screenshot_dir: Directory to save debug screenshots (default: current directory).
        """
        self.email = email or os.getenv("RIVERSIDE_LOGIN")
        self.password = password or os.getenv("RIVERSIDE_PASSWORD")
        self.headless = headless
        self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else Path.cwd()

        if not self.email or not self.password:
            raise ValueError(
                "Riverside credentials required. Set RIVERSIDE_LOGIN and RIVERSIDE_PASSWORD "
                "environment variables or pass email and password parameters."
            )

        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._playwright = None
        self._screenshot_count = 0

    def __enter__(self):
        """Context manager entry - start browser."""
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._page = self._browser.new_page()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close browser."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    @property
    def page(self) -> Page:
        """Get the current page, raising if not initialized."""
        if self._page is None:
            raise RuntimeError("Agent not initialized. Use 'with RiversideAgent() as agent:'")
        return self._page

    def screenshot(self, name: str = "screenshot") -> str:
        """Take a screenshot for debugging."""
        self._screenshot_count += 1
        filename = f"{self._screenshot_count:02d}_{name}.png"
        filepath = self.screenshot_dir / filename
        self.page.screenshot(path=str(filepath))
        print(f"Screenshot saved: {filepath}")
        return str(filepath)

    def login(self) -> None:
        """Log in to Riverside.fm."""
        print("Navigating to Riverside.fm...")
        self.page.goto("https://riverside.fm", wait_until="domcontentloaded")
        self.page.wait_for_timeout(3000)  # Give page time to render
        self.screenshot("homepage")

        # Try multiple login button selectors
        print("Looking for login button...")
        login_selectors = [
            "text=Log in",
            "text=Login",
            "text=Sign in",
            "a[href*='login']",
            "a[href*='signin']",
            "button:has-text('Log')",
            "[data-testid='login']",
        ]

        clicked = False
        for selector in login_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=2000):
                    print(f"Found login button with selector: {selector}")
                    elem.click()
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            # Maybe go directly to login URL
            print("Login button not found, navigating directly to login page...")
            self.page.goto("https://riverside.fm/login", wait_until="domcontentloaded")

        self.page.wait_for_timeout(3000)
        self.screenshot("login_page")

        # Wait for login form - try multiple selectors
        print("Waiting for login form...")
        email_selectors = [
            "input[type='email']",
            "input[name='email']",
            "input[placeholder*='email' i]",
            "input[placeholder*='Email' i]",
            "#email",
        ]

        email_input = None
        for selector in email_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=3000):
                    email_input = elem
                    print(f"Found email input with selector: {selector}")
                    break
            except Exception:
                continue

        if not email_input:
            self.screenshot("error_no_email_input")
            raise RuntimeError("Could not find email input field")

        # Fill in credentials
        print("Entering credentials...")
        email_input.fill(self.email)

        # Find and fill password
        password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "input[placeholder*='password' i]",
            "#password",
        ]

        password_input = None
        for selector in password_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=3000):
                    password_input = elem
                    print(f"Found password input with selector: {selector}")
                    break
            except Exception:
                continue

        if not password_input:
            self.screenshot("error_no_password_input")
            raise RuntimeError("Could not find password input field")

        password_input.fill(self.password)
        self.screenshot("credentials_filled")

        # Submit login form
        print("Submitting login...")
        submit_selectors = [
            "button[type='submit']",
            "button:has-text('Log in')",
            "button:has-text('Login')",
            "button:has-text('Sign in')",
            "input[type='submit']",
        ]

        for selector in submit_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=2000):
                    print(f"Found submit button with selector: {selector}")
                    elem.click()
                    break
            except Exception:
                continue

        # Wait for navigation after login
        print("Waiting for login to complete...")
        self.page.wait_for_timeout(5000)  # Wait for redirects
        self.screenshot("after_login")

        # Check if we're logged in by looking for dashboard indicators
        current_url = self.page.url
        print(f"Current URL after login: {current_url}")

        if "dashboard" in current_url or "home" in current_url or "studios" in current_url:
            print("Successfully logged in!")
        else:
            # Check for error messages
            error_elem = self.page.locator("[class*='error']").or_(
                self.page.locator("[role='alert']")
            )
            if error_elem.count() > 0:
                error_text = error_elem.first.text_content()
                raise RuntimeError(f"Login failed: {error_text}")
            print("Login may have succeeded, continuing...")

    def _open_new_session_form(self) -> None:
        """Navigate to Planner and open the new session form."""
        # Dismiss any announcement modal ("New! ...") that blocks sidebar clicks
        for _ in range(3):
            try:
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(500)
            except Exception:
                break

        print("Clicking on Planner in sidebar...")
        planner_selectors = [
            "text=Planner",
            "[aria-label*='Planner' i]",
            "a:has-text('Planner')",
            "button:has-text('Planner')",
        ]
        clicked = False
        for selector in planner_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=3000):
                    elem.click()
                    clicked = True
                    print(f"Clicked Planner with selector: {selector}")
                    break
            except Exception:
                continue

        if not clicked:
            raise RuntimeError("Could not find 'Planner' in sidebar")

        self.page.wait_for_timeout(2000)
        self.screenshot("schedule_page")

        # Click the "+ New" button in the top right of the calendar
        print("Looking for '+ New' button...")
        new_clicked = False
        try:
            buttons_with_new = self.page.locator("button").filter(has_text="New").all()
            for btn in buttons_with_new:
                try:
                    box = btn.bounding_box()
                    # The "+ New" button is in the top-right area
                    if box and box['x'] > 900 and box['y'] < 200:
                        print(f"Found '+ New' button at ({box['x']}, {box['y']})")
                        btn.click()
                        new_clicked = True
                        break
                except Exception:
                    continue
        except Exception as e:
            print(f"Error finding + New button: {e}")

        if not new_clicked:
            self.screenshot("error_no_new_session_button")
            raise RuntimeError("Could not find '+ New' button")

        self.page.wait_for_timeout(1000)
        self.screenshot("dropdown_menu")

        # After clicking "+ New", check if a dropdown or form panel appears
        # Try clicking "Session" from dropdown if it appears
        self._click_session_option()

        self.page.wait_for_timeout(1000)
        self.screenshot("new_session_form")

    def _click_session_option(self) -> None:
        """Click the 'Session' option in the new session dropdown."""
        session_selectors = [
            "[role='menuitem']:has-text('Session')",
            "[role='option']:has-text('Session')",
            "li:has-text('Session')",
            "a:has-text('Session')",
            "div[class*='menu'] >> text=Session",
            "div[class*='dropdown'] >> text=Session",
        ]

        clicked_session = False
        for selector in session_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=2000):
                    print(f"Found Session option with selector: {selector}")
                    elem.click()
                    clicked_session = True
                    break
            except Exception:
                continue

        if not clicked_session:
            # Fallback: find elements by position near the "+ New" button
            print("Trying fallback: looking for Session text elements...")
            session_elems = self.page.locator("text=Session").all()
            for elem in session_elems:
                try:
                    box = elem.bounding_box()
                    if box and box['x'] > 900 and box['y'] < 300:
                        print(f"Found Session element at ({box['x']}, {box['y']})")
                        elem.click()
                        clicked_session = True
                        break
                except Exception:
                    continue

        if not clicked_session:
            self.screenshot("error_no_session_option")
            raise RuntimeError("Could not find 'Session' option in dropdown")

        print("Clicked 'Session' option")

    def _fill_session_name(self, name: str) -> None:
        """Fill in the session name field."""
        print(f"Setting session name: {name}")
        name_filled = False

        name_selectors = [
            "input[placeholder*='Session name' i]",
            "[placeholder*='Session name' i]",
            "[data-testid='create-schedule-title'] input",
            "input[placeholder*='name' i]",
            "[data-testid*='title'] input",
            "input[name='name']",
        ]

        for selector in name_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=2000):
                    elem.click()
                    elem.fill(name)
                    print(f"Filled name input with selector: {selector}")
                    name_filled = True
                    break
            except Exception:
                continue

        if not name_filled:
            # Click near the "Session name" label and type
            print("Trying to click near 'Session name' label...")
            try:
                label = self.page.locator("text=Session name").first
                box = label.bounding_box()
                if box:
                    self.page.mouse.click(box['x'] + box['width'] / 2, box['y'] + 40)
                    self.page.wait_for_timeout(300)
                    self.page.keyboard.type(name)
                    print("Typed session name via label click")
                    name_filled = True
            except Exception as e:
                print(f"Label click failed: {e}")

        if not name_filled:
            self.screenshot("error_session_name")
            raise RuntimeError("Could not fill session name")

        self.page.wait_for_timeout(500)

    def _fill_description(self, description: str) -> None:
        """Fill in the session description field."""
        print(f"Setting description: {description}")
        desc_filled = False

        desc_selectors = [
            "textarea[placeholder*='Add description' i]",
            "textarea[placeholder*='Description' i]",
            "textarea[placeholder*='description' i]",
            "[data-testid*='description'] textarea",
            "[data-testid='create-schedule-description'] textarea",
            "textarea[name='description']",
            "textarea",
        ]

        for selector in desc_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=2000):
                    elem.click()
                    self.page.wait_for_timeout(200)
                    elem.fill(description)
                    print(f"Filled description with selector: {selector}")
                    desc_filled = True
                    break
            except Exception:
                continue

        if not desc_filled:
            # Try finding by label text and clicking near it
            print("Trying to find description by label...")
            try:
                desc_label = self.page.locator("text=Description").first
                if desc_label.is_visible(timeout=1000):
                    box = desc_label.bounding_box()
                    if box:
                        self.page.mouse.click(box['x'] + 100, box['y'] + 50)
                        self.page.wait_for_timeout(300)
                        self.page.keyboard.type(description)
                        print("Filled description by clicking near label")
                        desc_filled = True
            except Exception as e:
                print(f"Could not find description by label: {e}")

        if not desc_filled:
            print("Warning: Could not fill description field")

        self.screenshot("session_details_filled")

    def _set_timezone_pst(self) -> None:
        """Set the timezone to PST."""
        print("Setting timezone to PST...")

        tz_selectors = [
            "[data-testid*='timezone']",
            "[aria-label*='timezone' i]",
            "[aria-label*='time zone' i]",
            "button:has-text('EST')",
            "button:has-text('PST')",
            "button:has-text('PT')",
            "button:has-text('ET')",
            "[class*='timezone']",
        ]

        tz_clicked = False
        for selector in tz_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=1000):
                    print(f"Found timezone selector with: {selector}")
                    elem.click()
                    tz_clicked = True
                    break
            except Exception:
                continue

        if not tz_clicked:
            print("Trying to find timezone by position...")
            self.page.mouse.click(1000, 270)
            self.page.wait_for_timeout(500)
            self.screenshot("timezone_area_clicked")

        self.page.wait_for_timeout(800)
        self.screenshot("timezone_dropdown")

        # Look for Pacific Time option in dropdown
        pst_selectors = [
            "li:has-text('Pacific')",
            "li:has-text('PST')",
            "li:has-text('PT')",
            "li:has-text('Los Angeles')",
            "[role='option']:has-text('Pacific')",
            "[role='menuitem']:has-text('Pacific')",
            "text=Pacific Time",
            "text=(PT)",
        ]

        pst_selected = False
        for selector in pst_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=1500):
                    print(f"Found PST option with: {selector}")
                    elem.click()
                    pst_selected = True
                    break
            except Exception:
                continue

        if not pst_selected:
            print("Trying to type 'Pacific' to search...")
            self.page.keyboard.type("Pacific")
            self.page.wait_for_timeout(500)
            try:
                first_option = self.page.locator("li").first
                if first_option.is_visible(timeout=1000):
                    first_option.click()
                    pst_selected = True
            except Exception:
                pass

        if pst_selected:
            print("Timezone set to PST")
        else:
            print("Could not set timezone, pressing Escape and continuing...")
            self.page.keyboard.press("Escape")

        self.page.wait_for_timeout(500)
        self.screenshot("after_timezone")

    def _add_session_guests(self, guests: List[str]) -> None:
        """Add guests to the session via email."""
        print(f"Adding {len(guests)} guest(s) via email...")

        for guest_email in guests:
            print(f"Adding guest: {guest_email}")
            guest_filled = False

            # Use combined selector for faster matching
            combined_selector = (
                "input[placeholder='example@email.com'], "
                "input[placeholder*='example@email' i], "
                "input[placeholder*='Invite people via email' i], "
                "input[placeholder*='invite' i], "
                "[data-testid*='invite'] input, "
                "[data-testid*='guest'] input"
            )

            try:
                elem = self.page.locator(combined_selector).first
                if elem.is_visible(timeout=2000):
                    elem.click()
                    self.page.wait_for_timeout(200)
                    elem.fill(guest_email)
                    print("Filled guest email with combined selector")
                    guest_filled = True
            except Exception:
                pass

            # Fallback: try individual selectors with shorter timeout
            if not guest_filled:
                for selector in ["input[placeholder*='Invite people via email' i]", "input[placeholder*='email' i]"]:
                    try:
                        elem = self.page.locator(selector).first
                        if elem.is_visible(timeout=300):
                            elem.click()
                            self.page.wait_for_timeout(200)
                            elem.fill(guest_email)
                            print(f"Filled guest email with selector: {selector}")
                            guest_filled = True
                            break
                    except Exception:
                        continue

            if not guest_filled:
                # Try clicking by position
                print("Trying to fill guest email by position...")
                self.page.mouse.click(640, 389)
                self.page.wait_for_timeout(300)
                self.page.keyboard.type(guest_email)
                guest_filled = True

            # Press Enter to confirm the email entry
            self.page.keyboard.press("Enter")
            self.page.wait_for_timeout(500)

            if guest_filled:
                print(f"Added guest: {guest_email}")
            else:
                print(f"Warning: Could not add guest {guest_email}")

        self.screenshot("guests_added")

    def _set_session_date(self, target_date: datetime) -> None:
        """Set the session date using the calendar widget."""
        target_month_year = target_date.strftime("%B %Y")
        target_day = target_date.day
        print(f"Setting date to: {target_date.strftime('%m/%d/%Y')} ({target_month_year}, day {target_day})")

        # Click on the date field to open the calendar picker
        date_field = self.page.locator("[data-testid*='date']").first
        if not date_field.is_visible(timeout=1000):
            self.page.mouse.click(580, 270)
        else:
            date_field.click()
        self.page.wait_for_timeout(1000)
        self.screenshot("calendar_opened")

        # Navigate to the correct month
        self._navigate_calendar_to_month(target_date)

        # Click on the target day
        self.screenshot("calendar_month_selected")
        try:
            day_btn = self.page.locator(f"button[role='gridcell']:has-text('{target_day}')").filter(
                has_not=self.page.locator("[class*='Mui-disabled']")
            ).first
            if not day_btn.is_visible(timeout=1000):
                day_btn = self.page.locator(f"button:has-text('{target_day}')").first
            day_btn.click()
            print(f"Clicked on day {target_day}")
        except Exception as e:
            print(f"Could not click on day {target_day}: {e}")

        self.page.wait_for_timeout(500)
        self.screenshot("date_set")

    def _navigate_calendar_to_month(self, target_date: datetime) -> None:
        """Navigate the calendar to the target month."""
        target_month_year = target_date.strftime("%B %Y")

        for _ in range(12):
            try:
                header = self.page.locator("[class*='MuiPickersCalendarHeader']").or_(
                    self.page.locator("[class*='PrivatePickersFadeTransitionGroup']")
                ).or_(
                    self.page.locator("button:has-text('January')").or_(
                        self.page.locator("button:has-text('February')")
                    )
                )
                header_text = header.first.text_content(timeout=1000) if header.count() > 0 else ""
                print(f"Calendar header: {header_text}")

                if target_month_year in header_text or target_date.strftime("%B") in header_text:
                    print(f"Reached target month: {target_month_year}")
                    break
            except Exception as e:
                print(f"Could not read calendar header: {e}")

            # Click next month button
            try:
                next_btn = self.page.locator("[aria-label='Next month']").or_(
                    self.page.locator("[data-testid='ArrowRightIcon']").or_(
                        self.page.locator("button svg[data-testid='ArrowRightIcon']")
                    )
                ).first
                if next_btn.is_visible(timeout=1000):
                    next_btn.click()
                    print("Clicked next month")
                    self.page.wait_for_timeout(500)
                else:
                    self.page.mouse.click(700, 320)
                    self.page.wait_for_timeout(500)
            except Exception as e:
                print(f"Could not click next month: {e}")
                break

    def _set_session_time(self, start_datetime: datetime, duration_minutes: int) -> None:
        """Set the session start and end times."""
        start_time = start_datetime.strftime("%I:%M %p").lstrip("0")
        end_hour = start_datetime.hour + (duration_minutes // 60)
        end_ampm = "AM" if end_hour < 12 else "PM"
        end_hour_12 = end_hour % 12 or 12
        end_time = f"{end_hour_12}:{start_datetime.minute:02d} {end_ampm}"

        print(f"Setting start time: {start_time}")
        print(f"Setting end time: {end_time}")

        # Find the two time buttons in the form — they show the current time values
        # They appear side-by-side as clickable buttons (e.g. "05:00 PM" and "06:00 PM")
        self._select_time_from_button(0, start_time, "start")
        self._select_time_from_button(1, end_time, "end")

        self.screenshot("datetime_set")

    def _select_time_from_button(self, button_index: int, target_time: str, label: str) -> None:
        """Click the Nth time button in the session form, then pick from the dropdown list."""
        print(f"Opening {label} time dropdown...")

        # The time pickers are buttons containing time strings like "05:00 PM"
        # They sit inside the date/time row of the session creation form
        time_btn_selectors = [
            "button:has-text('AM'), button:has-text('PM')",
        ]

        # Collect all visible time buttons (AM or PM)
        try:
            all_time_btns = self.page.locator("button").filter(
                has=self.page.locator("text=/\\d{1,2}:\\d{2} (AM|PM)/")
            ).all()
            visible_btns = [b for b in all_time_btns if b.is_visible()]
            if len(visible_btns) > button_index:
                btn = visible_btns[button_index]
                print(f"Clicking time button {button_index}: '{btn.text_content()}'")
                btn.click()
            else:
                print(f"Not enough time buttons found ({len(visible_btns)}), falling back to position click")
                # Fallback positions based on new UI layout
                x_positions = [1078, 1192]
                self.page.mouse.click(x_positions[button_index], 199)
        except Exception as e:
            print(f"Error clicking time button: {e}")
            x_positions = [1078, 1192]
            self.page.mouse.click(x_positions[button_index], 199)

        self.page.wait_for_timeout(800)
        self.screenshot(f"{label}_time_dropdown")

        # Try to find the target time in the dropdown list
        time_option = self.page.locator(f"li:has-text('{target_time}')").first
        if time_option.is_visible(timeout=3000):
            time_option.click()
            print(f"Selected {label} time: {target_time}")
        else:
            print(f"Could not find '{target_time}' in list, trying to scroll...")
            dropdown = self.page.locator("ul[role='listbox']").or_(
                self.page.locator("[role='listbox']")
            ).first
            if dropdown.is_visible(timeout=1000):
                # Scroll down to find later times (8 PM is far down the list)
                dropdown.evaluate("el => el.scrollTop = el.scrollHeight * 0.7")
                self.page.wait_for_timeout(300)
                time_option = self.page.locator(f"li:has-text('{target_time}')").first
                if time_option.is_visible(timeout=1000):
                    time_option.click()
                    print(f"Selected {label} time after scroll: {target_time}")
                else:
                    print(f"Still could not find '{target_time}', pressing Escape")
                    self.page.keyboard.press("Escape")
            else:
                self.page.keyboard.press("Escape")

        self.page.wait_for_timeout(500)

    def _submit_session(self) -> str:
        """Submit the session form and return the session URL."""
        print("Creating session...")
        submit_selectors = [
            "button:has-text('Create')",
            "button:has-text('Save')",
            "button:has-text('Schedule')",
            "button:has-text('Confirm')",
            "button[type='submit']",
        ]

        for selector in submit_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.is_visible(timeout=2000):
                    print(f"Found submit button with selector: {selector}")
                    elem.click()
                    break
            except Exception:
                continue

        self.page.wait_for_timeout(5000)
        self.screenshot("session_created")

        session_url = self.page.url
        print(f"Session created! URL: {session_url}")
        return session_url

    def schedule_session(self, session: SessionDetails) -> str:
        """
        Schedule a new recording session.

        Args:
            session: Session details including name, description, date, and duration.

        Returns:
            URL of the created session.
        """
        print(f"Scheduling session: {session.name}")
        self.screenshot("dashboard_before_schedule")

        self._open_new_session_form()
        self._fill_session_name(session.name)
        self._fill_description(session.description)

        # Timezone already defaults to GMT-05:00 Chicago in the new UI — no change needed

        if session.guests:
            self._add_session_guests(session.guests)

        try:
            self._set_session_date(session.date)
        except Exception as e:
            print(f"Could not set date via calendar: {e}")

        try:
            self._set_session_time(session.date, session.duration_minutes)
        except Exception as e:
            print(f"Could not set time: {e}")

        return self._submit_session()

    def invite_guests(self, guest_emails: List[str]) -> None:
        """
        Invite guests to the session by email.

        Args:
            guest_emails: List of email addresses to invite.
        """
        print(f"Inviting {len(guest_emails)} guest(s)...")
        self.screenshot("before_invite_guests")

        # First, close the "Session scheduled!" modal if it's showing
        try:
            session_scheduled_modal = self.page.locator("text=Session scheduled!")
            if session_scheduled_modal.is_visible(timeout=2000):
                print("Closing 'Session scheduled!' modal...")
                # Click the X button in the modal (top-right corner)
                close_btn = self.page.locator("button:has-text('×')").or_(
                    self.page.locator("[aria-label='Close']").or_(
                        self.page.locator("[aria-label='close']")
                    )
                ).first
                if close_btn.is_visible(timeout=1000):
                    close_btn.click()
                else:
                    # Try clicking by position - X button is around (865, 264)
                    self.page.mouse.click(865, 264)
                self.page.wait_for_timeout(1000)
                print("Modal closed")
        except Exception as e:
            print(f"No session scheduled modal or error closing: {e}")

        self.screenshot("after_closing_modal")

        # Click on the session card to open session details
        print("Clicking on session card to access invite options...")
        try:
            # Look for the session card - it shows "No-one invited" text
            session_card = self.page.locator("text=No-one invited").or_(
                self.page.locator("[class*='session']").first
            )
            if session_card.is_visible(timeout=2000):
                session_card.click()
                self.page.wait_for_timeout(2000)
                print("Clicked on session card")
        except Exception as e:
            print(f"Could not click session card: {e}")

        self.screenshot("session_details_page")

        for email in guest_emails:
            print(f"Inviting guest: {email}")

            # Look for "Invite" or "Add Guest" button on the session page
            invite_clicked = False
            invite_selectors = [
                "button:has-text('Invite')",
                "button:has-text('Add Guest')",
                "button:has-text('Add guest')",
                "button:has-text('Add Participant')",
                "button:has-text('+ Invite')",
                "[data-testid*='invite']",
                "[aria-label*='invite' i]",
                "text=Invite guests",
                "text=+ Invite",
            ]

            for selector in invite_selectors:
                try:
                    elem = self.page.locator(selector).first
                    if elem.is_visible(timeout=2000):
                        print(f"Found invite button with: {selector}")
                        elem.click()
                        invite_clicked = True
                        break
                except Exception:
                    continue

            if not invite_clicked:
                print("Could not find invite button, trying to find it by position...")
                self.screenshot("looking_for_invite_button")

            self.page.wait_for_timeout(1500)
            self.screenshot("invite_dialog_opened")

            # Find the email input field in the invite dialog/form
            # The field has placeholder "example@email.com" in the "Invite via email" section
            # Use a combined selector to check all options at once (faster than sequential timeouts)
            email_filled = False
            combined_selector = (
                "input[placeholder='example@email.com'], "
                "input[placeholder*='example@email' i], "
                "input[type='email'], "
                "input[placeholder*='email' i], "
                "[data-testid*='email'] input, "
                "[data-testid*='guest'] input"
            )
            
            try:
                elem = self.page.locator(combined_selector).first
                if elem.is_visible(timeout=2000):
                    elem.click()
                    self.page.wait_for_timeout(200)
                    elem.fill(email)
                    print("Filled guest email with combined selector")
                    email_filled = True
            except Exception:
                pass
            
            # Fallback: try individual selectors with shorter timeout
            if not email_filled:
                email_selectors = [
                    "input[placeholder*='email' i]",
                    "input[name='email']",
                ]
                for selector in email_selectors:
                    try:
                        elem = self.page.locator(selector).first
                        if elem.is_visible(timeout=300):
                            elem.click()
                            self.page.wait_for_timeout(200)
                            elem.fill(email)
                            print(f"Filled guest email with selector: {selector}")
                            email_filled = True
                            break
                    except Exception:
                        continue

            if not email_filled:
                print(f"Warning: Could not fill email field for {email}")
                continue

            self.page.wait_for_timeout(500)
            self.screenshot("guest_email_filled")

            # Click send/invite button to confirm the invitation
            # The button says "Send invite"
            send_clicked = False
            send_selectors = [
                "button:has-text('Send invite')",
                "button:has-text('Send Invite')",
                "button:has-text('Send')",
                "button:has-text('Invite')",
                "button:has-text('Add')",
                "button[type='submit']",
            ]

            for selector in send_selectors:
                try:
                    elem = self.page.locator(selector).first
                    if elem.is_visible(timeout=2000):
                        print(f"Found send button with: {selector}")
                        elem.click()
                        send_clicked = True
                        break
                except Exception:
                    continue

            if send_clicked:
                print(f"Invitation sent to {email}")
            else:
                print(f"Warning: Could not send invitation to {email}")

            self.page.wait_for_timeout(2000)
            self.screenshot("after_invite_sent")

        print("Finished inviting guests")


    def run(self, session: SessionDetails) -> str:
        """
        Complete workflow: login and schedule a session.

        Args:
            session: Session details to schedule.

        Returns:
            URL of the created session.
        """
        self.login()
        return self.schedule_session(session)


def schedule_riverside_session(
    name: str,
    description: str,
    date: datetime,
    duration_minutes: int = 60,
    guests: Optional[List[str]] = None,
    headless: bool = False,
    screenshot_dir: Optional[str] = None
) -> str:
    """
    Convenience function to schedule a Riverside session.

    Args:
        name: Session name.
        description: Session description.
        date: Session date and start time.
        duration_minutes: Duration in minutes (default: 60).
        guests: List of guest email addresses to invite.
        headless: Whether to run browser in headless mode.
        screenshot_dir: Directory to save debug screenshots.

    Returns:
        URL of the created session.
    """
    session = SessionDetails(
        name=name,
        description=description,
        date=date,
        duration_minutes=duration_minutes,
        guests=guests
    )

    with RiversideAgent(headless=headless, screenshot_dir=screenshot_dir) as agent:
        return agent.run(session)
