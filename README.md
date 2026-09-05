# Why Houses Do That — automated Shorts pipeline

Faceless YouTube Shorts channel, fully automated on GitHub Actions. Two Shorts a day
(9 AM and 5 PM Eastern), a weekly analytics + optimization pass on Mondays, failure
alerts and a one-paragraph weekly email. Every asset is generated in-pipeline from our
own prompts and logged in `assets/license_log.csv`.

```
idea (content/topics.txt + Claude refill)
  -> script (content/calendar.json, 34 pre-written, auto-refills below 20)
  -> voiceover (ElevenLabs, with word timestamps)
  -> visuals (4 original cutaway illustrations via Replicate FLUX-schnell)
  -> captions (word-timed pop captions, burned in)
  -> assembly (ffmpeg, 1080x1920, Ken Burns + crossfades + hook title card)
  -> upload (YouTube Data API, A/B title variant, affiliate link in description)
  -> Monday: YouTube Analytics -> reweight hook styles + posting slots -> email summary
```

Running cost at 2 videos/day: ElevenLabs Starter $5 + Replicate ~$3 + Claude ~$3 = about $11/month.
GitHub Actions is free at this volume.

## One-time setup (about 30 minutes)

### 1. Put this repo on GitHub
Create a **private** repo named `whyhousesdothat` on the channel's GitHub account and push this folder to it.

### 2. Publish the OAuth app (removes the 7-day token expiry)
1. Repo -> Settings -> Pages -> Source: *Deploy from a branch*, branch `main`, folder `/docs`. Save.
   Your site is now `https://<github-username>.github.io/whyhousesdothat/`.
2. Google Search Console (https://search.google.com/search-console) -> Add property -> URL prefix ->
   paste that URL -> verify with the HTML-file method (drop the file into `docs/` and push).
3. Google Cloud console -> project `whyhousesdothat` -> Google Auth Platform -> Branding:
   - Application home page: the site URL
   - Privacy policy: `<site>/privacy.html`; Terms: `<site>/terms.html`
   - Authorized domains: `<github-username>.github.io`. Save.
4. Google Auth Platform -> Audience -> **Publish app** -> Confirm. (Unverified warning is fine.)

### 3. Get the YouTube refresh token (on your own computer)
```
pip install google-auth-oauthlib
python auth/get_refresh_token.py ~/Downloads/client_secret_XXXX.json
```
Sign in as **whyhousesdothat@gmail.com**, click through the "unverified app" warning, approve.
It prints `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.

### 4. Gmail app password (for alerts and the weekly email)
Google Account (channel Gmail) -> Security -> 2-Step Verification must be on -> App passwords -> create one
named "pipeline". That 16-character string is `GMAIL_APP_PASSWORD`.

### 5. Paste secrets and variables
Repo -> Settings -> Secrets and variables -> Actions.

**Secrets** (tab "Secrets"):
| Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | from console.anthropic.com |
| `ELEVENLABS_API_KEY` | from elevenlabs.io |
| `REPLICATE_API_TOKEN` | from replicate.com |
| `YT_CLIENT_ID` | printed by step 3 |
| `YT_CLIENT_SECRET` | printed by step 3 |
| `YT_REFRESH_TOKEN` | printed by step 3 |
| `GMAIL_APP_PASSWORD` | from step 4 |
| `ALERT_EMAIL` | the address you want alerts sent to (can be your personal email) |

**Variables** (tab "Variables"):
| Name | Value |
|---|---|
| `GMAIL_ADDRESS` | `whyhousesdothat@gmail.com` |
| `PUBLISH_PRIVACY` | `private` for now; change to `public` after step 7 |
| `ELEVENLABS_VOICE_ID` | optional; leave blank for the default "Daniel" voice |
| `AMAZON_TAG` | leave blank until Amazon Associates approves you |

### 6. Test run
Repo -> Actions -> `publish-short` -> Run workflow -> set `dry_run` = `true`.
When it finishes (about 4 minutes), open the run and download the `latest-short` artifact to watch it.
Then run it again with `dry_run` = `false`; the video uploads as **private**. Check it in YouTube Studio.

### 7. YouTube API compliance audit (makes uploads public)
Brand-new API projects have uploads locked to private until Google audits the project. Submit
https://support.google.com/youtube/contact/yt_api_form — describe it as: *"Single-channel tool
that uploads the operator's own original videos and reads the operator's own analytics. No third-party
users, no data storage beyond the operator's channel."* Takes a few days to two weeks. When approved,
set the `PUBLISH_PRIVACY` variable to `public`. Everything uploaded before that can be made public
manually in YouTube Studio in one batch.

### 8. Enable the schedule
Nothing to do; the cron in `.github/workflows/publish.yml` is live once the repo exists. GitHub pauses
scheduled workflows on repos with no activity for 60 days, and the pipeline commits state on every
run, so that never triggers.

## Where things live
- `content/calendar.json` — the script queue. Edit freely; `status: queued` ones get published FIFO
  (biased toward winning hook styles once data exists).
- `content/topics.txt` — the topic bank the refill pulls from. Add lines anytime.
- `content/state.json` — published videos, A/B results, hook and slot weights.
- `assets/license_log.csv` — every voice and image asset, its source, and the prompt that produced it.
- `logs/` — one file per month.
- `pipeline/script_gen.py` — the system prompt that defines the channel voice. Change the channel here.

## Monetization layer
Amazon Associates links are already wired: once `AMAZON_TAG` is set, every video's description gets a
tagged search link for the product named in that script (`affiliate_search`) plus the required disclosure.
Apply at affiliate-program.amazon.com after the channel has some traffic; you need 3 sales in 180 days to
keep the account, so applying too early wastes the attempt.

## Weekly email
One paragraph: views, subscriber change, retention, revenue, best slot, what the optimizer changed.
Failure alerts arrive only when a run fails, with the traceback.

## Manual levers (all optional)
- Run `publish-short` by hand anytime for an extra post.
- Change the cron lines to move posting times; the optimizer reports which slot wins.
- `PUBLISH_PRIVACY=unlisted` if you want to review a batch before going public.
