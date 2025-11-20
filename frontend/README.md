# StyleGenie Frontend (Vite + React)

Single-page app for StyleGenie. Handles auth, onboarding, wardrobe uploads, AI recommendations UI, stylist marketplace, and a documentation hub that links design/system assets.

## Quickstart
```bash
cd frontend
npm install
npm run dev
```
Dev server runs on `http://localhost:5173`.

## Prerequisites
- Node.js 18+ (LTS recommended)
- npm 9+ (comes with Node)

## Environment
Create `frontend/.env` (name values with `VITE_` prefix so Vite exposes them):
```dotenv
VITE_API_BASE_URL=http://localhost:8000
VITE_FRONTEND_BASE_URL=http://localhost:5173

# Cloudinary unsigned upload preset for wardrobe digitization
VITE_CLOUDINARY_CLOUD_NAME=<your-cloud>
VITE_CLOUDINARY_UPLOAD_PRESET=<unsigned-preset>

# Links shown on /documentation
VITE_SYSTEM_DESIGN_URL=https://...
VITE_FIGMA_FILE_URL=https://...
VITE_PRODUCT_REQUIREMENTS_URL=https://...
VITE_PITCH_DECK_URL=https://...

# Optional demo creds surfaced in the docs page
VITE_STAGING_CLIENT_EMAIL=demo@example.com
VITE_STAGING_CLIENT_PASSWORD=SafePass123
VITE_STAGING_STYLIST_EMAIL=stylist@example.com
VITE_STAGING_STYLIST_PASSWORD=SafePass123
```
If `VITE_API_BASE_URL` is empty, the app falls back to `https://stylegenie-backend.up.railway.app`.

## Feature map (UI routes)
- `/` – marketing landing with CTA to register/browse stylists.
- `/login`, `/register` – auth flows with JWTs stored in context.
- `/dashboard` – client profile editor (body/face shape, tones) + wardrobe upload cards (Cloudinary).
- `/recommendations` – fetches AI outfit suggestions for a selected occasion/datetime; displays generated looks and progress.
- `/stylists` – curated stylist list with bios, expertise tags, and ratings.
- `/documentation` – team roster, system design/pitch links, and optional staging credentials.

## Scripts
- `npm run dev` – start Vite dev server.
- `npm run build` – production bundle to `dist/`.
- `npm run build:dev` – production build using development mode flags.
- `npm run preview` – serve the built app locally.
- `npm run lint` – ESLint (React, hooks, TypeScript).

## API integration
- All API calls use `src/lib/api.ts` and the `VITE_API_BASE_URL` plus `/client` and `/stylist` routes from the Django backend.
- Cloudinary uploads use `src/lib/cloudinary.ts` and the `VITE_CLOUDINARY_*` envs.
- Auth/session state lives in `context/AuthContext` with React Query caching data.

## Project structure (high level)
- `src/pages` – route screens (Landing, Auth, Dashboard, Stylists, Recommendations, Documentation).
- `src/components` – shared UI (Navigation, forms, cards, toasts) built on shadcn-ui/Radix.
- `src/context` – `AuthContext` for JWT/session handling.
- `src/lib` – API + Cloudinary helpers, utils.
- `src/assets` – hero/marketing imagery.

## Build & deploy
- `npm run build` emits `dist/`; deploy to static hosts (Vercel/Netlify/S3/CloudFront).
- Supply `VITE_*` vars at build time (host env panel or CI secrets). Vercel/Netlify require redeploy after env changes.
- Backend must allow your frontend origin in `ALLOWED_HOSTS`/CORS/CSRF (see backend README). Point `VITE_API_BASE_URL` at the deployed API.
- Configure caching/headers at your CDN; keep SPA fallback to `index.html`.

## Production checklist
- Lock Node.js to an LTS version in your CI/CD runner.
- Build: `npm ci && npm run lint && npm run build`.
- Set `VITE_API_BASE_URL` to the HTTPS backend URL; avoid mixing HTTP/HTTPS to prevent mixed content.
- Set `VITE_CLOUDINARY_*` to a hardened unsigned or signed preset before going live.
- If hosting and API are on different domains, confirm cookies/headers aren’t blocked by CORS.
