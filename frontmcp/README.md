# ConvoNet FrontMCP Server

> Based on the official FrontMCP "Welcome" guide: https://docs.agentfront.dev/getting-started/welcome

This directory contains a TypeScript-first FrontMCP server that exposes ConvoNet agent tools (team todos + calendar events) over the MCP protocol. It satisfies the hackathon rule that every project must ship at least one MCP integration.

## Structure
- `src/server.ts` – matches the doc's `@FrontMcp`/`@App`/`tool` pattern.
- `package.json` / `tsconfig.json` – minimal tooling for `ts-node` or `tsc` builds.

## Environment Variables
```bash
CONVONET_API_BASE=https://hjlees.com
FRONTMCP_SERVICE_TOKEN=<service JWT for server-side calls>
FRONTEGG_BASE_URL=https://your-workspace.frontegg.com
```

`FRONTMCP_SERVICE_TOKEN` can be any backend JWT (issued by ConvoNet or Frontegg) that has access to the protected `/convonet_todo/api` routes. When the MCP client authenticates via the remote Frontegg login, `ctx.auth?.token` replaces this service token automatically.

## Commands
```bash
cd frontmcp
npm install
npm run dev       # ts-node live server
npm run build && npm start  # compile + run
```

## Deploying to Frontegg FrontMCP
1. In the Frontegg portal, create a new FrontMCP workspace/app.
2. Upload the compiled `dist/server.js` or point your hosted MCP worker at this repo.
3. Set the same environment variables inside the Frontegg deployment.

Refer back to the [FrontMCP welcome guide](https://docs.agentfront.dev/getting-started/welcome) for more advanced decorators, hooks, and DI patterns if you extend the server with Airia or additional Conv0Net tools.
