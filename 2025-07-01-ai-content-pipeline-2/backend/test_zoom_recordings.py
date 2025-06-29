import os
import json
import requests

MEETING_ID = "83674506960"

def get_zoom_access_token():
    # Read the access token from zoom_token.json (created by oauth_setup_claude.py)
    token_path = os.path.join(os.path.dirname(__file__), "zoom_token.json")
    if not os.path.exists(token_path):
        raise RuntimeError("zoom_token.json not found. Run oauth_setup_claude.py first.")
    with open(token_path, "r") as f:
        token_data = json.load(f)
    return token_data["access_token"]

def get_recordings(meeting_id, access_token):
    url = f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def main():
    access_token = get_zoom_access_token()
    data = get_recordings(MEETING_ID, access_token)
    print(f"Meeting ID: {MEETING_ID}")
    print("Recording files:")
    for rec in data.get("recording_files", []):
        print(f"  - id: {rec.get('id')}, type: {rec.get('recording_type')}, file_type: {rec.get('file_type')}, download_url: {rec.get('download_url')}")

if __name__ == "__main__":
    main()