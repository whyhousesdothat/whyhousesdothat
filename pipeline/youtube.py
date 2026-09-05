import datetime as dt
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from . import config

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/yt-analytics.readonly",
          "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"]

def _creds():
    return Credentials(None, refresh_token=config.YT_REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token",
                       client_id=config.YT_CLIENT_ID, client_secret=config.YT_CLIENT_SECRET, scopes=SCOPES)

def upload(mp4, title, description, tags, privacy):
    yt = build("youtube", "v3", credentials=_creds(), cache_discovery=False)
    body = {"snippet": {"title": title[:100], "description": description[:4900], "tags": tags[:30],
                        "categoryId": "26", "defaultLanguage": "en"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}}
    media = MediaFileUpload(mp4, chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return resp["id"]

def set_thumbnail(video_id, jpg):
    yt = build("youtube", "v3", credentials=_creds(), cache_discovery=False)
    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(jpg)).execute()
    except Exception:
        pass  # custom thumbnails require phone verification; Shorts pick a frame anyway

def channel_stats():
    yt = build("youtube", "v3", credentials=_creds(), cache_discovery=False)
    r = yt.channels().list(part="statistics", mine=True).execute()
    return r["items"][0]["statistics"]

def analytics(days=7):
    ya = build("youtubeAnalytics", "v2", credentials=_creds(), cache_discovery=False)
    end = dt.date.today(); start = end - dt.timedelta(days=days)
    base = dict(ids="channel==MINE", startDate=str(start), endDate=str(end))
    tot = ya.reports().query(**base, metrics="views,estimatedMinutesWatched,averageViewPercentage,subscribersGained").execute()
    per_video = ya.reports().query(**base, dimensions="video", sort="-views", maxResults=50,
                                   metrics="views,averageViewPercentage,likes").execute()
    revenue = None
    try:
        rv = ya.reports().query(**base, metrics="estimatedRevenue").execute()
        revenue = rv["rows"][0][0] if rv.get("rows") else 0.0
    except Exception:
        pass
    row = tot["rows"][0] if tot.get("rows") else [0, 0, 0, 0]
    return {"views": row[0], "minutes": row[1], "avg_view_pct": row[2], "subs_gained": row[3],
            "revenue": revenue, "videos": [{"id": r[0], "views": r[1], "avg_view_pct": r[2], "likes": r[3]}
                                           for r in per_video.get("rows", [])]}
