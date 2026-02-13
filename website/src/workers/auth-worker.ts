/**
 * Google OAuth Authentication Worker (Cloudflare Workers)
 *
 * Handles:
 * - Google OAuth 2.0 login flow
 * - Email allowlist enforcement (ALLOWED_EMAILS)
 * - Session management via KV
 * - User records via D1
 *
 * Protected routes check the session cookie. Public routes pass through.
 * Only emails listed in ALLOWED_EMAILS can access protected content.
 */

interface Env {
  SESSION_STORE: KVNamespace;
  DB: D1Database;
  GOOGLE_CLIENT_ID: string;
  GOOGLE_CLIENT_SECRET: string;
  GOOGLE_REDIRECT_URI: string;
  ALLOWED_EMAILS: string;
}

interface GoogleUserInfo {
  id: string;
  email: string;
  name: string;
  picture: string;
}

interface SessionData {
  userId: string;
  email: string;
  name: string;
}

const SESSION_TTL = 86400; // 24 hours

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    const corsHeaders = {
      'Access-Control-Allow-Origin': url.origin,
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      switch (url.pathname) {
        case '/auth/google':
          return handleLogin(env);
        case '/auth/callback':
          return await handleCallback(request, env);
        case '/auth/session':
          return await handleSessionCheck(request, env);
        case '/auth/logout':
          return await handleLogout(request, env);
        default:
          return new Response('Not Found', { status: 404 });
      }
    } catch (error) {
      console.error('Auth error:', error);
      return new Response('Internal Server Error', { status: 500 });
    }
  },
};

function handleLogin(env: Env): Response {
  const state = crypto.randomUUID();
  const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');

  authUrl.searchParams.set('client_id', env.GOOGLE_CLIENT_ID);
  authUrl.searchParams.set('redirect_uri', env.GOOGLE_REDIRECT_URI);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('scope', 'openid email profile');
  authUrl.searchParams.set('state', state);
  authUrl.searchParams.set('prompt', 'select_account');

  return Response.redirect(authUrl.toString(), 302);
}

async function handleCallback(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const code = url.searchParams.get('code');

  if (!code) {
    return new Response('Missing authorization code', { status: 400 });
  }

  const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      code,
      client_id: env.GOOGLE_CLIENT_ID,
      client_secret: env.GOOGLE_CLIENT_SECRET,
      redirect_uri: env.GOOGLE_REDIRECT_URI,
      grant_type: 'authorization_code',
    }),
  });

  if (!tokenResponse.ok) {
    return new Response('Token exchange failed', { status: 401 });
  }

  const tokens = (await tokenResponse.json()) as { access_token: string };

  const userInfoResponse = await fetch(
    'https://www.googleapis.com/oauth2/v2/userinfo',
    { headers: { Authorization: `Bearer ${tokens.access_token}` } }
  );

  if (!userInfoResponse.ok) {
    return new Response('Failed to fetch user info', { status: 502 });
  }

  const userInfo: GoogleUserInfo = await userInfoResponse.json();

  const allowedEmails = env.ALLOWED_EMAILS.split(',').map((e) =>
    e.trim().toLowerCase()
  );

  if (!allowedEmails.includes(userInfo.email.toLowerCase())) {
    return new Response(`Access denied. ${userInfo.email} is not authorized.`, {
      status: 403,
    });
  }

  await env.DB.prepare(
    `INSERT INTO users (id, email, name, picture_url, updated_at)
     VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
     ON CONFLICT(id) DO UPDATE SET
       name = excluded.name,
       picture_url = excluded.picture_url,
       updated_at = CURRENT_TIMESTAMP`
  )
    .bind(userInfo.id, userInfo.email, userInfo.name, userInfo.picture)
    .run();

  const sessionToken = crypto.randomUUID();
  const sessionData: SessionData = {
    userId: userInfo.id,
    email: userInfo.email,
    name: userInfo.name,
  };

  await env.SESSION_STORE.put(
    `session:${sessionToken}`,
    JSON.stringify(sessionData),
    { expirationTtl: SESSION_TTL }
  );

  return new Response(null, {
    status: 302,
    headers: {
      Location: '/',
      'Set-Cookie': `session=${sessionToken}; HttpOnly; Secure; SameSite=Lax; Max-Age=${SESSION_TTL}; Path=/`,
    },
  });
}

async function handleSessionCheck(
  request: Request,
  env: Env
): Promise<Response> {
  const cookie = request.headers.get('Cookie') || '';
  const sessionToken = cookie
    .split(';')
    .find((c) => c.trim().startsWith('session='))
    ?.split('=')[1]
    ?.trim();

  if (!sessionToken) {
    return Response.json({ authenticated: false }, { status: 401 });
  }

  const sessionRaw = await env.SESSION_STORE.get(`session:${sessionToken}`);
  if (!sessionRaw) {
    return Response.json({ authenticated: false }, { status: 401 });
  }

  const session: SessionData = JSON.parse(sessionRaw);
  return Response.json({
    authenticated: true,
    email: session.email,
    name: session.name,
  });
}

async function handleLogout(request: Request, env: Env): Promise<Response> {
  const cookie = request.headers.get('Cookie') || '';
  const sessionToken = cookie
    .split(';')
    .find((c) => c.trim().startsWith('session='))
    ?.split('=')[1]
    ?.trim();

  if (sessionToken) {
    await env.SESSION_STORE.delete(`session:${sessionToken}`);
  }

  return new Response(null, {
    status: 302,
    headers: {
      Location: '/',
      'Set-Cookie':
        'session=; HttpOnly; Secure; SameSite=Lax; Max-Age=0; Path=/',
    },
  });
}
