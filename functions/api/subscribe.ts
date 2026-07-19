// Cloudflare Pages Function: Newsletter subscription handler
// POST /api/subscribe → validates email → stores in KV → returns JSON
// Rate limited to 5 req/min per IP to prevent abuse

interface Env {
  NEWSLETTER: KVNamespace;
}

export async function onRequestPost(context: { request: Request; env: Env }) {
  const { request, env } = context;

  // Only accept POST
  if (request.method !== 'POST') {
    return json({ error: 'Method not allowed' }, 405);
  }

  // Rate limiting (simple IP-based, 5 per minute)
  const ip = request.headers.get('cf-connecting-ip') || 'unknown';
  const rateKey = `rate:${ip}`;
  const recentSubmissions = parseInt(await env.NEWSLETTER.get(rateKey) || '0');
  if (recentSubmissions >= 5) {
    return json({ error: 'Too many requests. Please try again later.' }, 429);
  }
  await env.NEWSLETTER.put(rateKey, String(recentSubmissions + 1), { expirationTtl: 60 });

  // Parse email
  let email: string;
  try {
    const body = await request.json() as { email: string };
    email = (body.email || '').trim().toLowerCase();
  } catch {
    return json({ error: 'Invalid request body' }, 400);
  }

  // Validate email format
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ error: 'Please enter a valid email address.' }, 400);
  }

  // Block disposable/temp email domains (basic list)
  const blockedDomains = ['mailinator.com', 'tempmail.com', '10minutemail.com', 'guerrillamail.com', 'sharklasers.com', 'yopmail.com'];
  const domain = email.split('@')[1];
  if (blockedDomains.includes(domain)) {
    return json({ error: 'Please use a permanent email address.' }, 400);
  }

  // Check duplicate
  const existing = await env.NEWSLETTER.get(`sub:${email}`);
  if (existing) {
    return json({ message: 'already_subscribed' });
  }

  // Store subscriber
  await env.NEWSLETTER.put(`sub:${email}`, JSON.stringify({
    email,
    subscribed_at: new Date().toISOString(),
    ip,
    lang: request.headers.get('accept-language')?.split(',')[0] || '',
  }));

  return json({ message: 'subscribed' });
}

function json(data: Record<string, unknown>, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'content-type': 'application/json',
      'access-control-allow-origin': '*',
      'access-control-allow-methods': 'POST, OPTIONS',
      'access-control-allow-headers': 'Content-Type',
    },
  });
}

// Handle CORS preflight
export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'access-control-allow-origin': '*',
      'access-control-allow-methods': 'POST, OPTIONS',
      'access-control-allow-headers': 'Content-Type',
      'access-control-max-age': '86400',
    },
  });
}
