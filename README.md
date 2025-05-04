# spoty-star
A Spotify Flask Server automating spotify workflows

# Dev Reproduction

1. React with vite using TailwindCSS set up just like at [tailwindcss.com](https://v3.tailwindcss.com/docs/guides/vite)
2. DaisyUI installed just like here: [daisyui.com](https://daisyui.com/docs/install/)
   1. also aded to `tailwind.config.js`:

```js
  plugins: [
    require("daisyui"),
  ],
```

# Build & Run

## Build Backend

The Flask backend needs an `.env` using the following structure:

```yml
CLIENT_ID = <from_spotify_dev>
CLIENT_SECRET = <from_spotify_dev>
SECRET_KEY = <create_random_long_string>
```

# Run

- **in Prod:** run Flask server via`python3 main.py`, uses the static files of React built by vite (`npm run build`) as specified in the `main.py::app` variable
- **in Dev**: `npm run dev` running, all `api/` requests are proxied to the concurrently running `python3 main.py` Flask server (as specified in `vite.config.ts`):

```js
  server: {
    proxy: {
      '/api': 'http://localhost:5001',
    }
  }
```

# Debugging Nightmares

- localhost bei redirect und /callback nicht gleich behandelt wie `127.0.0.1`
- it seems that tracks of a given playlist can only be fetched in chunks of 100 (since there is no skip_duplicate param when adding to playlists...)