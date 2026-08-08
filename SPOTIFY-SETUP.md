# Spotify live widget setup

The "Now Playing" widget in the profile README is powered by
[spotify-github-profile](https://spotify-github-profile.vercel.app).
It needs **your Spotify username** to render your current listening activity.

## Steps

1. Open https://spotify-github-profile.vercel.app
2. Click **Connect with Spotify** and authorise the app (it only reads your
   listening activity).
3. After connecting, the site shows your personalised URL. It contains your
   Spotify username (your public handle) in the `uid=` parameter.
4. Copy that username.

## Update the README

Edit `README.md` and replace **both** occurrences of `YOUR_SPOTIFY_UID`
(the `<a href>` and the `<img src>` inside the "Now Playing" section) with
your username.

```
https://spotify-github-profile.vercel.app/api/view?uid=YOUR_SPOTIFY_UID&cover_image=true&theme=novatide&bar_color=53b14f&bar_color_cover=true
```

- `cover_image=true` — show the album art of the current track.
- `theme=novatide` — dark neon theme that matches this profile.
- `bar_color=53b14f` — green progress bar; change the hex to any colour you like.

## Notes

- The widget shows the currently playing track and updates automatically
  while you listen.
- If nothing is playing it shows a "Not listening right now" state.
- You only need to do this once.
