# Spotify live widget setup

The "Now Playing" widget in the profile README is powered by
[spotify-github-profile](https://spotify-github-profile.vercel.app).
It needs **your Spotify username** to render your current listening activity.

## Status

This profile is already configured with the public uid `31y7htruozzrnh2fraukjakcg4ii`
(the widget renders at `spotify-github-profile.kittinanx.com`). If the widget ever
breaks or you want to change the look, follow the steps below.

## Steps

1. Open https://spotify-github-profile.vercel.app
2. Click **Connect with Spotify** and authorise the app (it only reads your
   listening activity).
3. After connecting, the site shows your personalised URL. It contains your
   Spotify username (your public handle) in the `uid=` parameter.
4. Copy that username.

## Update the README

The "Now Playing" section in `README.md` already uses this URL (uid filled in):

```
https://spotify-github-profile.kittinanx.com/api/view?uid=31y7htruozzrnh2fraukjakcg4ii&cover_image=true&theme=default&show_offline=false&background_color=1099c6&interchange=false&profanity=false&hide_remaster=false&bar_color_cover=true&bar_color=b8c412
```

- `cover_image=true` — show the album art of the current track.
- `background_color=1099c6` — widget background (sky blue); change the hex to any colour.
- `bar_color=b8c412` — progress bar colour (chartreuse); change the hex to any colour you like.
- `theme=default` — card layout; options include `novatide`, `cyberpunk`, `dark`.
- `redirect=true` (in the link) — clicking the widget opens the track on Spotify.

## Notes

- The widget shows the currently playing track and updates automatically
  while you listen.
- If nothing is playing it shows a "Not listening right now" state.
- You only need to do this once.
