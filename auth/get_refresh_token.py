"""One-time: run this on your own computer to get a refresh token for the channel.

    pip install google-auth-oauthlib
    python auth/get_refresh_token.py path/to/client_secret_xxx.json

It opens a browser; sign in as the channel Gmail and approve. It prints three
values to paste into GitHub -> Settings -> Secrets and variables -> Actions -> Secrets.
"""
import sys, json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
]

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python auth/get_refresh_token.py client_secret.json")
    flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    cfg = json.load(open(sys.argv[1]))["installed"]
    print("\nPaste these into GitHub Actions secrets:\n")
    print("YT_CLIENT_ID     =", cfg["client_id"])
    print("YT_CLIENT_SECRET =", cfg["client_secret"])
    print("YT_REFRESH_TOKEN =", creds.refresh_token)
    if not creds.refresh_token:
        print("\nNo refresh token returned. Remove the app from https://myaccount.google.com/permissions and run again.")

if __name__ == "__main__":
    main()
