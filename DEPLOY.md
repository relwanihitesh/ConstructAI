# Deploy ConstructAI on Render

[Deploy with Render](https://render.com/deploy?repo=https://github.com/ikshitjain/ConstructAI)

1. Sign in to Render. Open the deployment link above.
2. Review the `constructai` web service. Instance type: **Free**.
3. Deploy the Blueprint and wait for its status to become **Live**.
4. Open the generated HTTPS `onrender.com` address. Use this as the demo link in SkillWallet.

The tracked `frontend/dist` is served by FastAPI, so no separate frontend host or CORS setup is needed. When changing the UI, run `npm ci` and `npm run build` in `frontend`, then commit the updated dist files.

If creating a Web Service manually, use:

| Setting | Value |
|---|---|
| Repository | `https://github.com/ikshitjain/ConstructAI` |
| Branch | `main` |
| Runtime | Python 3 |
| Root directory | Leave blank |
| Build command | `pip install -r backend/requirements.txt` |
| Start command | `uvicorn main:app --app-dir backend --host 0.0.0.0 --port $PORT --proxy-headers` |
| Health check | `/api/health` |
| Instance | Free |
| Environment | `PYTHON_VERSION=3.13.5`, `PUBLIC_DEMO=1`, `CONSTRUCT_DATA_DIR=/tmp/constructai-data` |

Public demo mode scopes saved reports to an anonymous browser session using an HttpOnly cookie. Each visitor sees only reports created in that browser session. Clearing the cookie loses access to those reports. It is not an authenticated account system.

The free deployment uses temporary storage. Reports can disappear on restart, redeploy or sleep; download important reports. Render free services sleep after inactivity and may take about a minute to wake up. See [Render free service limits](https://render.com/docs/free).

The initial deployment uses demo mode without provider credentials. Add authentication and request limits before enabling shared paid AI credentials on a public service. Provider keys belong in Render environment variables, never GitHub. Persistent multi-user storage is a separate production upgrade.

Verify `/api/health`, load the dashboard, generate a planner worksheet and reopen it from Saved reports. Verify in a second browser that the first visitor's history is not visible.
