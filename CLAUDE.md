# tarotmom-media

Daily "card of the day" videos for the Instagram account @tarotmomdaily (owner: Tahir).
Videos are served publicly through GitHub Pages at
`https://tahiryasti.github.io/tarotmom-media/videos/<date>.mp4`, which is the URL handed to Instagram.

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
4. Commit spec + video, push to `main`. Wait until the video URL returns HTTP 200 (Pages takes 1–3 min).
5. Post on Instagram via Windsor.ai: connector `instagram`, account `17841429505297492`, action
   `create_video_post` with `video_url` and a caption (hook sentence, card meaning in 1–2 lines, the
   call to action, then ~8 hashtags such as #tarot #tarotreading #dailytarot #cardoftheday #pickacard
   #spiritualtok #manifestation #tarotmom).
6. Append a line to `posted.md`: `- <date> | <CARD NAME> | <media id or error>`, commit and push.
7. Send Tahir the video file and the caption so he can also upload it to TikTok.
