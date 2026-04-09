import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Agents } from '../../src/resources/agents/index.js';
import { Messages } from '../../src/resources/agents/messages.js';
import { Conversations } from '../../src/resources/agents/conversations.js';
import { Analytics } from '../../src/resources/agents/analytics.js';
import { Evaluations } from '../../src/resources/agents/evaluations.js';
import { Access } from '../../src/resources/agents/access.js';
import { Tools } from '../../src/resources/agents/tools.js';
import { A2A } from '../../src/resources/agents/a2a.js';
import type { HttpClient } from '../../src/core/http-client.js';

// ---------------------------------------------------------------------------
// Mock HttpClient
// ---------------------------------------------------------------------------

function createMockHttpClient() {
  return {
    baseURL: 'https://api.sandbox.prisme.ai/v2',
    get: vi.fn().mockResolvedValue({}),
    post: vi.fn().mockResolvedValue({}),
    put: vi.fn().mockResolvedValue({}),
    patch: vi.fn().mockResolvedValue({}),
    delete: vi.fn().mockResolvedValue({}),
    request: vi.fn().mockResolvedValue({}),
    requestRaw: vi.fn().mockResolvedValue(new Response()),
  } as unknown as HttpClient & {
    get: ReturnType<typeof vi.fn>;
    post: ReturnType<typeof vi.fn>;
    put: ReturnType<typeof vi.fn>;
    patch: ReturnType<typeof vi.fn>;
    delete: ReturnType<typeof vi.fn>;
    request: ReturnType<typeof vi.fn>;
    requestRaw: ReturnType<typeof vi.fn>;
  };
}

const WS_ID = 'ws-123';
const PREFIX = `/workspaces/${WS_ID}/webhooks`;

// ---------------------------------------------------------------------------
// Agents
// ---------------------------------------------------------------------------

describe('Agents', () => {
  let http: ReturnType<typeof createMockHttpClient>;
  let agents: Agents;

  beforeEach(() => {
    http = createMockHttpClient();
    agents = new Agents(http, WS_ID);
  });

  describe('list', () => {
    it('returns a PageIterator for agents', () => {
      const iter = agents.list();
      expect(iter).toBeDefined();
      expect(typeof iter.toArray).toBe('function');
    });

    it('passes params as query to paginator', () => {
      const iter = agents.list({ search: 'test' } as any);
      expect(iter).toBeDefined();
    });
  });

  describe('create', () => {
    it('calls POST on agents path', async () => {
      const params = { name: 'Test Agent' };
      http.post.mockResolvedValueOnce({ id: 'a1', name: 'Test Agent' });

      const result = await agents.create(params as any);

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/agents`, params, undefined);
      expect(result).toEqual({ id: 'a1', name: 'Test Agent' });
    });
  });

  describe('get', () => {
    it('calls GET on specific agent path', async () => {
      http.get.mockResolvedValueOnce({ id: 'a1', name: 'Agent' });

      const result = await agents.get('a1');

      expect(http.get).toHaveBeenCalledWith(`${PREFIX}/agents/a1`);
      expect(result).toEqual({ id: 'a1', name: 'Agent' });
    });
  });

  describe('update', () => {
    it('calls PATCH on specific agent path', async () => {
      const params = { name: 'Updated' };
      http.patch.mockResolvedValueOnce({ id: 'a1', name: 'Updated' });

      const result = await agents.update('a1', params as any);

      expect(http.patch).toHaveBeenCalledWith(`${PREFIX}/agents/a1`, params);
      expect(result).toEqual({ id: 'a1', name: 'Updated' });
    });
  });

  describe('delete', () => {
    it('calls DELETE on specific agent path', async () => {
      http.delete.mockResolvedValueOnce(undefined);

      await agents.delete('a1');

      expect(http.delete).toHaveBeenCalledWith(`${PREFIX}/agents/a1`, undefined);
    });
  });

  describe('publish', () => {
    it('calls POST on publish path', async () => {
      http.post.mockResolvedValueOnce({ id: 'a1', status: 'published' });

      const result = await agents.publish('a1');

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/agents/a1/publish`, undefined, undefined);
      expect(result).toEqual({ id: 'a1', status: 'published' });
    });
  });

  describe('discardDraft', () => {
    it('calls POST on discard-draft path', async () => {
      http.post.mockResolvedValueOnce({ id: 'a1', status: 'active' });

      const result = await agents.discardDraft('a1');

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/agents/a1/discard-draft`, undefined, undefined);
      expect(result).toEqual({ id: 'a1', status: 'active' });
    });
  });

  describe('discovery', () => {
    it('calls PATCH on discovery path with params', async () => {
      const params = { enabled: true, categories: ['cat1'], featured: false };
      http.patch.mockResolvedValueOnce({ id: 'a1', discovery: params });

      const result = await agents.discovery('a1', params);

      expect(http.patch).toHaveBeenCalledWith(`${PREFIX}/agents/a1/discovery`, params);
      expect(result).toEqual({ id: 'a1', discovery: params });
    });
  });

  describe('export', () => {
    it('calls GET on export path', async () => {
      http.get.mockResolvedValueOnce({ config: {} });

      const result = await agents.export('a1');

      expect(http.get).toHaveBeenCalledWith(`${PREFIX}/agents/a1/export`);
      expect(result).toEqual({ config: {} });
    });
  });

  describe('import', () => {
    it('calls POST on import path with config', async () => {
      const config = { name: 'Imported Agent' };
      http.post.mockResolvedValueOnce({ id: 'a2', name: 'Imported Agent' });

      const result = await agents.import(config);

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/agents/import`, config, undefined);
      expect(result).toEqual({ id: 'a2', name: 'Imported Agent' });
    });
  });

  describe('sub-resources are wired', () => {
    it('has messages sub-resource', () => {
      expect(agents.messages).toBeInstanceOf(Messages);
    });

    it('has conversations sub-resource', () => {
      expect(agents.conversations).toBeInstanceOf(Conversations);
    });

    it('has tools sub-resource', () => {
      expect(agents.tools).toBeInstanceOf(Tools);
    });

    it('has access sub-resource', () => {
      expect(agents.access).toBeInstanceOf(Access);
    });

    it('has analytics sub-resource', () => {
      expect(agents.analytics).toBeInstanceOf(Analytics);
    });

    it('has evaluations sub-resource', () => {
      expect(agents.evaluations).toBeInstanceOf(Evaluations);
    });

    it('has a2a sub-resource', () => {
      expect(agents.a2a).toBeInstanceOf(A2A);
    });
  });
});

// ---------------------------------------------------------------------------
// Messages
// ---------------------------------------------------------------------------

describe('Messages', () => {
  let http: ReturnType<typeof createMockHttpClient>;
  let messages: Messages;

  beforeEach(() => {
    http = createMockHttpClient();
    messages = new Messages(http, WS_ID);
  });

  describe('send', () => {
    it('calls POST on messages path', async () => {
      const params = { text: 'Hello' };
      http.post.mockResolvedValueOnce({ text: 'Hi there' });

      const result = await messages.send('a1', params as any);

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/agents/a1/messages`, params, undefined);
      expect(result).toEqual({ text: 'Hi there' });
    });
  });

  describe('stream', () => {
    it('calls requestRaw with SSE headers and returns SSEStream', async () => {
      const mockResponse = new Response('data: {"type":"delta"}\n\n', {
        headers: { 'content-type': 'text/event-stream' },
      });
      http.requestRaw.mockResolvedValueOnce(mockResponse);

      const params = { text: 'Hello' };
      const stream = await messages.stream('a1', params as any);

      expect(http.requestRaw).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'POST',
          path: `${PREFIX}/agents/a1/messages/stream`,
          body: params,
          headers: { accept: 'text/event-stream' },
        }),
      );
      expect(stream).toBeDefined();
      expect(typeof stream[Symbol.asyncIterator]).toBe('function');
    });
  });
});

// ---------------------------------------------------------------------------
// Conversations
// ---------------------------------------------------------------------------

describe('Conversations', () => {
  let http: ReturnType<typeof createMockHttpClient>;
  let conversations: Conversations;

  beforeEach(() => {
    http = createMockHttpClient();
    conversations = new Conversations(http, WS_ID);
  });

  describe('list', () => {
    it('returns a PageIterator', () => {
      const iter = conversations.list();
      expect(iter).toBeDefined();
      expect(typeof iter.toArray).toBe('function');
    });
  });

  describe('create', () => {
    it('calls POST on conversations path', async () => {
      const params = { agentId: 'a1' };
      http.post.mockResolvedValueOnce({ id: 'c1' });

      const result = await conversations.create(params as any);

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/conversations`, params, undefined);
      expect(result).toEqual({ id: 'c1' });
    });

    it('works without params', async () => {
      http.post.mockResolvedValueOnce({ id: 'c1' });

      const result = await conversations.create();

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/conversations`, undefined, undefined);
      expect(result).toEqual({ id: 'c1' });
    });
  });

  describe('get', () => {
    it('calls GET on specific conversation path', async () => {
      http.get.mockResolvedValueOnce({ id: 'c1' });

      const result = await conversations.get('c1');

      expect(http.get).toHaveBeenCalledWith(`${PREFIX}/conversations/c1`);
      expect(result).toEqual({ id: 'c1' });
    });
  });

  describe('update', () => {
    it('calls PATCH on specific conversation path', async () => {
      const params = { title: 'Updated' };
      http.patch.mockResolvedValueOnce({ id: 'c1', title: 'Updated' });

      const result = await conversations.update('c1', params as any);

      expect(http.patch).toHaveBeenCalledWith(`${PREFIX}/conversations/c1`, params);
      expect(result).toEqual({ id: 'c1', title: 'Updated' });
    });
  });

  describe('delete', () => {
    it('calls DELETE on specific conversation path', async () => {
      http.delete.mockResolvedValueOnce(undefined);

      await conversations.delete('c1');

      expect(http.delete).toHaveBeenCalledWith(`${PREFIX}/conversations/c1`, undefined);
    });
  });

  describe('messages', () => {
    it('returns a PageIterator for conversation messages', () => {
      const iter = conversations.messages('c1');
      expect(iter).toBeDefined();
      expect(typeof iter.toArray).toBe('function');
    });

    it('passes pagination params', () => {
      const iter = conversations.messages('c1', { page: 2, limit: 5 });
      expect(iter).toBeDefined();
    });
  });

  describe('share', () => {
    it('calls POST on share path', async () => {
      const params = { email: 'user@example.com' };
      http.post.mockResolvedValueOnce(undefined);

      await conversations.share('c1', params as any);

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/conversations/c1/share`, params, undefined);
    });
  });
});

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

describe('Analytics', () => {
  let http: ReturnType<typeof createMockHttpClient>;
  let analytics: Analytics;

  beforeEach(() => {
    http = createMockHttpClient();
    analytics = new Analytics(http, WS_ID);
  });

  describe('get', () => {
    it('calls GET on analytics path with params', async () => {
      const params = { from: '2024-01-01', to: '2024-01-31' };
      http.get.mockResolvedValueOnce({ data: [] });

      const result = await analytics.get('a1', params as any);

      expect(http.get).toHaveBeenCalledWith(
        `${PREFIX}/agents/a1/analytics`,
        params,
      );
      expect(result).toEqual({ data: [] });
    });

    it('works without params', async () => {
      http.get.mockResolvedValueOnce({ data: [] });

      const result = await analytics.get('a1');

      expect(http.get).toHaveBeenCalledWith(
        `${PREFIX}/agents/a1/analytics`,
        undefined,
      );
      expect(result).toEqual({ data: [] });
    });
  });
});

// ---------------------------------------------------------------------------
// Evaluations
// ---------------------------------------------------------------------------

describe('Evaluations', () => {
  let http: ReturnType<typeof createMockHttpClient>;
  let evaluations: Evaluations;

  beforeEach(() => {
    http = createMockHttpClient();
    evaluations = new Evaluations(http, WS_ID);
  });

  describe('list', () => {
    it('returns a PageIterator', () => {
      const iter = evaluations.list('a1');
      expect(iter).toBeDefined();
      expect(typeof iter.toArray).toBe('function');
    });

    it('passes pagination params', () => {
      const iter = evaluations.list('a1', { page: 1, limit: 10 });
      expect(iter).toBeDefined();
    });
  });

  describe('create', () => {
    it('calls POST with evaluation params', async () => {
      const params = {
        name: 'Test Eval',
        dataset: [{ input: 'hello', expectedOutput: 'hi' }],
      };
      http.post.mockResolvedValueOnce({ id: 'e1', name: 'Test Eval' });

      const result = await evaluations.create('a1', params);

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/agents/a1/evaluations`, params, undefined);
      expect(result).toEqual({ id: 'e1', name: 'Test Eval' });
    });
  });
});

// ---------------------------------------------------------------------------
// Access
// ---------------------------------------------------------------------------

describe('Access', () => {
  let http: ReturnType<typeof createMockHttpClient>;
  let access: Access;

  beforeEach(() => {
    http = createMockHttpClient();
    access = new Access(http, WS_ID);
  });

  describe('list', () => {
    it('returns a PageIterator', () => {
      const iter = access.list('a1');
      expect(iter).toBeDefined();
    });

    it('passes params', () => {
      const iter = access.list('a1', { page: 1, limit: 10 } as any);
      expect(iter).toBeDefined();
    });
  });

  describe('grant', () => {
    it('calls POST to grant access', async () => {
      const params = { userId: 'u1', role: 'viewer' };
      http.post.mockResolvedValueOnce({ id: 'acc1' });

      const result = await access.grant('a1', params as any);

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/agents/a1/access`, params, undefined);
      expect(result).toEqual({ id: 'acc1' });
    });
  });

  describe('revoke', () => {
    it('calls DELETE on access entry', async () => {
      http.delete.mockResolvedValueOnce(undefined);

      await access.revoke('a1', 'acc1');

      expect(http.delete).toHaveBeenCalledWith(`${PREFIX}/agents/a1/access/acc1`, undefined);
    });
  });

  describe('requestAccess', () => {
    it('calls POST on access-requests path', async () => {
      http.post.mockResolvedValueOnce({ id: 'req1', status: 'pending' });

      const result = await access.requestAccess('a1');

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/agents/a1/access-requests`, undefined, undefined);
      expect(result).toEqual({ id: 'req1', status: 'pending' });
    });
  });

  describe('listRequests', () => {
    it('returns a PageIterator', () => {
      const iter = access.listRequests('a1');
      expect(iter).toBeDefined();
    });
  });

  describe('handleRequest', () => {
    it('calls POST with approve action', async () => {
      http.post.mockResolvedValueOnce({ id: 'req1', status: 'approved' });

      const result = await access.handleRequest('a1', 'req1', { action: 'approve' } as any);

      expect(http.post).toHaveBeenCalledWith(
        `${PREFIX}/agents/a1/access-requests/req1/approve`,
        undefined,
        undefined,
      );
      expect(result).toEqual({ id: 'req1', status: 'approved' });
    });

    it('calls POST with reject action', async () => {
      http.post.mockResolvedValueOnce({ id: 'req1', status: 'rejected' });

      const result = await access.handleRequest('a1', 'req1', { action: 'reject' } as any);

      expect(http.post).toHaveBeenCalledWith(
        `${PREFIX}/agents/a1/access-requests/req1/reject`,
        undefined,
        undefined,
      );
      expect(result).toEqual({ id: 'req1', status: 'rejected' });
    });
  });
});

// ---------------------------------------------------------------------------
// Tools
// ---------------------------------------------------------------------------

describe('Tools', () => {
  let http: ReturnType<typeof createMockHttpClient>;
  let tools: Tools;

  beforeEach(() => {
    http = createMockHttpClient();
    tools = new Tools(http, WS_ID);
  });

  describe('list', () => {
    it('returns a PageIterator', () => {
      const iter = tools.list();
      expect(iter).toBeDefined();
    });

    it('passes params', () => {
      const iter = tools.list({ page: 1, limit: 5 } as any);
      expect(iter).toBeDefined();
    });
  });

  describe('create', () => {
    it('calls POST on tools path', async () => {
      const params = { name: 'My Tool', type: 'function' };
      http.post.mockResolvedValueOnce({ id: 't1' });

      const result = await tools.create(params as any);

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/tools`, params, undefined);
      expect(result).toEqual({ id: 't1' });
    });
  });

  describe('get', () => {
    it('calls GET on specific tool path', async () => {
      http.get.mockResolvedValueOnce({ id: 't1', name: 'Tool' });

      const result = await tools.get('t1');

      expect(http.get).toHaveBeenCalledWith(`${PREFIX}/tools/t1`);
      expect(result).toEqual({ id: 't1', name: 'Tool' });
    });
  });
});

// ---------------------------------------------------------------------------
// A2A
// ---------------------------------------------------------------------------

describe('A2A', () => {
  let http: ReturnType<typeof createMockHttpClient>;
  let a2a: A2A;

  beforeEach(() => {
    http = createMockHttpClient();
    a2a = new A2A(http, WS_ID);
  });

  describe('send', () => {
    it('calls POST on a2a send path', async () => {
      const params = { message: { text: 'Hello' } };
      http.post.mockResolvedValueOnce({ taskId: 't1' });

      const result = await a2a.send('a1', params as any);

      expect(http.post).toHaveBeenCalledWith(`${PREFIX}/agents/a1/a2a/send`, params, undefined);
      expect(result).toEqual({ taskId: 't1' });
    });
  });

  describe('sendSubscribe', () => {
    it('calls requestRaw with SSE headers and returns SSEStream', async () => {
      const mockResponse = new Response('data: {}\n\n', {
        headers: { 'content-type': 'text/event-stream' },
      });
      http.requestRaw.mockResolvedValueOnce(mockResponse);

      const params = { message: { text: 'Hello' } };
      const stream = await a2a.sendSubscribe('a1', params as any);

      expect(http.requestRaw).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'POST',
          path: `${PREFIX}/agents/a1/a2a/send-subscribe`,
          body: params,
          headers: { accept: 'text/event-stream' },
        }),
      );
      expect(stream).toBeDefined();
      expect(typeof stream[Symbol.asyncIterator]).toBe('function');
    });
  });

  describe('getCard', () => {
    it('calls GET on a2a card path', async () => {
      http.get.mockResolvedValueOnce({ name: 'Agent Card' });

      const result = await a2a.getCard('a1');

      expect(http.get).toHaveBeenCalledWith(`${PREFIX}/agents/a1/a2a/card`);
      expect(result).toEqual({ name: 'Agent Card' });
    });
  });

  describe('getExtendedCard', () => {
    it('calls GET on extended card path', async () => {
      http.get.mockResolvedValueOnce({ name: 'Extended Card', tools: [] });

      const result = await a2a.getExtendedCard('a1');

      expect(http.get).toHaveBeenCalledWith(`${PREFIX}/agents/a1/a2a/card/extended`);
      expect(result).toEqual({ name: 'Extended Card', tools: [] });
    });
  });
});
