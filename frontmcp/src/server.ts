import 'dotenv/config';
import { FrontMcp, App, tool } from '@frontmcp/sdk';
import { z } from 'zod';
import fetch from 'cross-fetch';

const API_BASE = process.env.CONVONET_API_BASE || 'https://hjlees.com';
const SERVICE_TOKEN = process.env.FRONTMCP_SERVICE_TOKEN;

const authHeader = (ctxToken?: string) => {
  const token = ctxToken || SERVICE_TOKEN;
  if (!token) {
    throw new Error('No bearer token available for Convonet API call');
  }
  return { Authorization: `Bearer ${token}` };
};

const ListTeamTodos = tool({
  name: 'list-team-todos',
  description: 'Fetch the latest todos for a team from ConvoNet',
  inputSchema: z.object({
    teamId: z.string().uuid(),
  }),
})(async (input, ctx) => {
  const response = await fetch(`${API_BASE}/convonet_todo/api/team-todos?team_id=${input.teamId}`, {
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(ctx.auth?.token),
    },
  });
  if (!response.ok) {
    throw new Error(`Team todos failed: ${response.statusText}`);
  }
  const data = await response.json();
  return { todos: data.todos || data.items || [] };
});

const CreateCalendarEvent = tool({
  name: 'create-calendar-event',
  description: 'Create a calendar event using ConvoNet calendar MCP tool',
  inputSchema: z.object({
    teamId: z.string().uuid(),
    title: z.string(),
    description: z.string().optional(),
    eventFrom: z.string(),
    eventTo: z.string(),
  }),
})(async (input, ctx) => {
  const response = await fetch(`${API_BASE}/convonet_todo/api/team-todos/calendar`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(ctx.auth?.token),
    },
    body: JSON.stringify({
      team_id: input.teamId,
      title: input.title,
      description: input.description,
      event_from: input.eventFrom,
      event_to: input.eventTo,
    }),
  });
  if (!response.ok) {
    throw new Error(`Calendar create failed: ${response.statusText}`);
  }
  return { message: 'Event created', event: await response.json() };
});

@App({
  id: 'convonet-agent-tools',
  name: 'ConvoNet Agent Tools',
  tools: [ListTeamTodos, CreateCalendarEvent],
})
class AgentToolsApp {}

@FrontMcp({
  info: { name: 'ConvoNet FrontMCP', version: '0.1.0' },
  apps: [AgentToolsApp],
  auth: {
    type: 'remote',
    name: 'frontegg',
    baseUrl: process.env.FRONTEGG_BASE_URL,
  },
})
export default class ConvoNetServer {}
