# Frontegg FrontMCP Integration (Hackathon Edition)

These steps follow the official instructions in the Frontegg integration guide  
[`https://portal.frontegg.com/development/frontegg-integration-guide`](https://portal.frontegg.com/development/frontegg-integration-guide).

## 1. Provision FrontMCP Workspace
1. Open the guide in the Frontegg portal and click **Create workspace** (or reuse the existing `convonet` workspace shown in the portal screenshot).
2. Enable the **Authentication**, **Self-served portal**, and **Management & analytics** modules so the MCP console can manage tenants for the hackathon demo.
3. In **AI Agents (Beta)**, create a new MCP product named `ConvoNet Voice Agent`.

## 2. Generate Credentials
Inside the workspace:
1. Navigate to **Configurations → Applications → Machine-to-machine** and a create client named `convonet-backend`.
2. Copy the generated values into the new environment variables:
   - `FRONTEGG_CLIENT_ID`
   - `FRONTEGG_CLIENT_SECRET`
3. In **Keys & domains**, copy:
   - `FRONTEGG_BASE_URL` (workspace URL)
   - `FRONTEGG_JWKS_URL` (under “OpenID / JWKS”)
   - `FRONTEGG_ISSUER`
4. Under **Login box → Domains**, add `https://hjlees.com` and `http://localhost:5000` so the hosted login works in prod and local dev.

## 3. Configure Redirects & OAuth App
1. Still in the guide, create a **Hosted Login** flow.
2. Add redirect URIs:
   - `https://hjlees.com/callback/frontegg`
   - `http://localhost:5000/callback/frontegg`
3. Under **User pools**, enable email and tenant attributes so the JWT exposes `email`, `tenantId`, and `preferred_username`.

## 4. Update ConvoNet Environment
Add the following variables (see also `convonet/ENVIRONMENT_VARIABLES.md`):

```bash
FRONTEGG_CLIENT_ID=xxxxxxxx
FRONTEGG_CLIENT_SECRET=xxxxxxxx
FRONTEGG_BASE_URL=https://your-workspace.frontegg.com
FRONTEGG_JWKS_URL=https://your-workspace.frontegg.com/.well-known/jwks.json
FRONTEGG_AUDIENCE=xxxxxxxx   # usually equals CLIENT_ID
FRONTEGG_ISSUER=https://your-workspace.frontegg.com
FRONTEGG_DEFAULT_TEAM_ID=<UUID of demo team in Convonet DB>
```

`FRONTEGG_DEFAULT_TEAM_ID` links newly-created SSO users to an existing Convonet team so collaboration routes keep working.

## 5. Backend Wiring
The new module `convonet/integrations/frontegg_client.py`:
- validates FrontMCP JWTs with the JWKS endpoint (RS256),
- upserts a local `users_convonet` entry by email,
- auto-enrolls the user into the team referenced by `FRONTEGG_DEFAULT_TEAM_ID`,
- returns the enriched identity to Flask via `request.current_user`.

`convonet/security/auth.py` now checks for Frontegg tokens first, then falls back to the legacy HS256 tokens.

## 6. Frontend / Callbacks
- Point your login button to the Frontegg hosted login URL (the guide gives the exact URL snippet) or drop in the MCP widget script.
- Ensure `/callback/frontegg` exchanges the authorization code and stores `access_token` in `localStorage` just like the existing JWT (front-end work tracked separately).

## 7. FrontMCP Server (docs.agentfront.dev)
Following the [FrontMCP welcome guide](https://docs.agentfront.dev/getting-started/welcome), the new `frontmcp/src/server.ts` uses `@FrontMcp`, `@App`, and `tool` decorators to expose ConvoNet APIs. Deploy it inside Frontegg FrontMCP or run locally with `npm run dev`.

## 8. Testing Checklist
1. `source .env && flask run`
2. Login via Frontegg → copy the returned access token from dev tools.
3. Hit `/api/team-todos` with `Authorization: Bearer <frontegg token>` and confirm 200 OK.
4. Verify DB created/updated a `users_convonet` row for the Frontegg email.
5. Join the hackathon demo team automatically (membership record inserted).

Following the portal guide plus these repo changes gives you a production-ready FrontMCP story for the hackathon demo.


