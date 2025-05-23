# Spoty Star

![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Jinja](https://img.shields.io/badge/jinja-white.svg?style=for-the-badge&logo=jinja&logoColor=black)

![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
![DaisyUI](https://img.shields.io/badge/daisyui-5A0EF8?style=for-the-badge&logo=daisyui&logoColor=white)

A React web UI to sort your Spotify playlists relying on a Flask backend.

# Dev Reproduction

## Basic Setup

1. React with vite using TailwindCSS set up just like at [tailwindcss.com](https://v3.tailwindcss.com/docs/guides/vite)
2. DaisyUI installed just like here: [daisyui.com](https://daisyui.com/docs/install/)
   1. also aded to `tailwind.config.js`:

```js
  plugins: [
    require("daisyui"),
  ],
```

## Linting via pre-commit hook using [Husky](https://typicode.github.io/husky/get-started.html)

Used [this tutorial](https://scottsauber.com/2021/06/01/using-husky-git-hooks-and-lint-staged-with-nested-folders/).

Instead of creating `.lintstagedrc` added the following to `package.json`:

```json
"lint-staged": {
  "*.{js,ts,jsx,tsx}": "prettier --write"
}
```

Now all staged .tsx, .js, ... files will get linted.
Manually lint files with `npx lint-staged`.

# Build & Run

## Run

- **in Prod:** run Flask server via`python3 main.py`, uses the static files of React built by vite (`npm run build`) as specified in the `main.py::app` variable
- **in Dev**: `npm run dev` running, all `api/` requests are proxied to the concurrently running `python3 main.py` Flask server (as specified in `vite.config.ts`):

```js
  server: {
    proxy: {
      '/api': 'http://localhost:5001',
    }
  }
```

## Build Backend

The Flask backend needs an `.env` using the following structure:

```yml
CLIENT_ID = <from_spotify_dev>
CLIENT_SECRET = <from_spotify_dev>
SECRET_KEY = <create_random_long_string>
IS_DEV = <weather_api_should_redirect_to_react>
```

<hr>

# Debugging Nightmares

- localhost bei redirect und /callback nicht gleich behandelt wie `127.0.0.1`
- it seems that tracks of a given playlist can only be fetched in chunks of 100 (since there is no skip_duplicate param when adding to playlists...)