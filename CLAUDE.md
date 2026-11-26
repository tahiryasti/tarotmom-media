# tarotmom-media

Daily "card of the day" videos for the Instagram account @tarotmomdaily (owner: Tahir).
Instagram fetches each video from the raw GitHub URL
`https://raw.githubusercontent.com/tahiryasti/tarotmom-media/main/videos/<date>.mp4` (this worked on 2026-11-25).

## Daily routine
1. Pick today's card. Check `posted.md` and do not repeat a card used in the last 14 days.
2. Write `specs/<YYYY-MM-DD>.json` (date in America/New_York):
   ```json
   {"numeral": "XIX", "name": "THE SUN", "symbol": "sun",
    "hook": ["Stop scrolling.", "This message is for you."],
    "messages": [["Line one."], ["Line two a", "line two b"], ["Short closing line."]],
    "cta_top": ["Type \"YES\"", "if you're ready for it"]}
   ```
   - `symbol` is one of: star, sun, moon, heart, crown, eye, wheel, lightning, infinity, cup, sword.
   - English, warm, hopeful, short. Each message line at most ~28 characters; 3 messages; at most 2 lines each.
   - Vary the hook and the call to action every day. No health, money, legal or "guaranteed" predictions.
3. Render: `tools/render.sh specs/<date>.json videos/<date>.mp4` (needs python3 with Pillow, and ffmpeg).
4. Commit spec + video, push to `main`. Wait about 30 seconds after the push.
5. Post on Instagram via Windsor.ai: connector `instagram`, account `17841429505297492`, action
   `create_video_post` with `video_url` and a caption (hook sentence, card meaning in 1–2 lines, the
   call to action, then ~8 hashtags such as #tarot #tarotreading #dailytarot #cardoftheday #pickacard
   #spiritualtok #manifestation #tarotmom).
6. Append a line to `posted.md`: `- <date> | <CARD NAME> | <media id or error>`, commit and push.
7. Post the same video on TikTok (account tarotmomdaily, already signed in) through the built-in browser
   on Tahir's computer (mcp__remote-devices__Claude_Browser__browser_repl). What works (2026-11-25):
   - In a github.com tab (e.g. https://github.com/tahiryasti/tarotmom-media), `page.evaluate` a
     `fetch("/tahiryasti/tarotmom-media/raw/main/videos/<date>.mp4")`, base64 it and keep it in
     `window.__b64`; read it back into the REPL in 500,000-character slices. (TikTok's own page cannot
     fetch the file: its CSP blocks it. raw.githubusercontent.com pages block fetch too.)
   - Open https://www.tiktok.com/tiktokstudio/upload, wait for `input[type="file"]`, push the base64 into
     the page in slices of at most 140,000 characters (evaluate arguments are capped at 150,000), then
     build a File, put it on the input with a DataTransfer and dispatch `change`.
   - If a "Turn on automatic content checks?" dialog appears, press **Cancel** (do not change account
     settings). Press "Got it" on tips.
   - Caption: focus the first `[contenteditable="true"]`, put the caret at the end with a Range, press
     Backspace until it is empty (the field starts with the file name), then `keyboard.insertText` the
     caption, press Escape. Leave "When to post: Now" and "Everyone". Click the button named "Post";
     the toast "Video published" confirms it.
   - If the computer or browser can't be reached, or TikTok asks to log in, skip TikTok and tell Tahir.
8. Tell Tahir in Turkish what was posted where.

## Pick-a-card routine (Mon / Wed / Fri, from 2026-12-03)
Part of the 90-day growth roadmap (Claude Doc "90 Günlük Büyüme Yol Haritası"). Runs in addition to the daily card.
1. Choose 3 different tarot cards (none used in the daily videos of the last 7 days or the last pick-a-card). One theme per video, rotating: general message, love, career/purpose, "what you need to hear", the week ahead.
2. Write `specs/<date>-pick.json` (see `specs/example-pick.json`):
   `{"type":"pickacard","hook":[2 lines],"piles":[{"numeral","name","symbol","messages":[[1 line],[1–2 lines]]} x3],"cta":["Which one did you pick?","Comment 1, 2 or 3"]}`
   Same text rules as the daily card (English, warm, ≤28 chars per line, no health/money/legal/guaranteed predictions). Vary the hook each time.
3. Render: `tools/render_pickacard.sh specs/<date>-pick.json videos/<date>-pick.mp4` (26 s).
4. Commit + push, wait ~30 s, post to Instagram (Windsor.ai `create_video_post`, video_url `.../videos/<date>-pick.mp4`) and TikTok exactly as in steps 5 and 7 above.
   Caption: the hook, "Pause and pick 1, 2 or 3 — then watch your card", the 3 card names, "Comment your number below 👇", then ~8 hashtags (#pickacard #tarotreading #tarot #pickacardreading #tarotcommunity #spiritualtok #tarotmom #dailytarot).
5. Append `- <date> | PICK: <CARD1> / <CARD2> / <CARD3> | <IG media id> , TikTok posted/skipped` to `posted.md`, commit + push.
