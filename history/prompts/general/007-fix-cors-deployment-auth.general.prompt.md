---
id: 007
title: Fix Sign-in/Sign-up After Deployment
stage: general
date: 2026-01-19
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: nida.nasarr
command: implement plan
labels: ["deployment", "cors", "authentication", "vercel", "hugging-face"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend_deploy/Fullstack-to-do-app/main.py
tests:
  - N/A (manual verification via browser DevTools)
---

## Prompt

Implement the following plan:

# Plan: Fix Sign-in/Sign-up After Deployment

## Problem
Authentication (sign-in/sign-up) fails after deploying frontend to Vercel and backend to Hugging Face. The browser blocks requests due to CORS and misconfigured API URLs.

## Your Deployment URLs
- **Frontend (Vercel):** `https://fullstack-todo-app.vercel.app`
- **Backend (Hugging Face):** `https://nidanasar123-fullstack-to-do-app.hf.space`

## Root Causes

1. **CORS blocks requests** - Backend only allows `localhost`, not your Vercel URL
2. **API URL defaults to localhost** - Frontend tries to call `localhost:8000` instead of HF Space
3. **Environment variables not set** - Production env vars missing in both platforms

---

## Solution (4 Steps)

### Step 1: Update CORS in Backend (Code Change)
### Step 2: Set Vercel Environment Variables (Dashboard)
### Step 3: Set Hugging Face Environment Variables (Dashboard)
### Step 4: Redeploy

## Response snapshot

1. **Updated CORS configuration** in `backend_deploy/Fullstack-to-do-app/main.py:44-49` to add `https://fullstack-todo-app.vercel.app` to the `allow_origins` list.

2. **Provided Vercel env var instructions:**
   - `NEXT_PUBLIC_API_URL` = `https://nidanasar123-fullstack-to-do-app.hf.space/api/v1`
   - `BETTER_AUTH_SECRET` = `92R79JkLYyR389z6aynG3KL0JWNrEB4y`

3. **Provided Hugging Face env var instructions:**
   - `DATABASE_URL` = Neon PostgreSQL connection string
   - `BETTER_AUTH_SECRET` = `92R79JkLYyR389z6aynG3KL0JWNrEB4y`
   - `BETTER_AUTH_URL` = `https://fullstack-todo-app.vercel.app`
   - `ENVIRONMENT` = `production`

4. **Redeploy instructions:** Push CORS change to trigger HF rebuild; Vercel auto-redeploys on env var changes.

## Outcome

- ✅ Impact: Enables cross-origin authentication between Vercel frontend and HF Space backend
- 🧪 Tests: Manual verification via browser DevTools (Network tab, Console for CORS errors)
- 📁 Files: 1 file modified (main.py CORS config)
- 🔁 Next prompts: Verify deployment works, test sign-up/sign-in flow
- 🧠 Reflection: CORS is a common deployment issue when frontend and backend are on different domains

## Evaluation notes (flywheel)

- Failure modes observed: None - straightforward implementation
- Graders run and results (PASS/FAIL): N/A (deployment fix)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider using environment variable for production URL instead of hardcoding
