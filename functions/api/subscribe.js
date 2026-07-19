// Cloudflare Pages Function: Newsletter subscription handler
// POST /api/subscribe → validates email → stores in KV → returns JSON

export async function onRequestPost(context) {
  const { request, env } = context;

  // Rate limiting (per IP, 5 per minute)
  const ip = request.headers.get('cf-connecting-ip') || 'unknown';
  const rateKey = 'rate:' + ip;
  const recentCount = parseInt(await env.NEWSLETTER.get(rateKey) || '0');
  if (recentCount >= 5) {
    return json({ error: 'Too many requests. Please try again later.' }, 429);
  }
  await env.NEWSLETTER.put(rateKey, String(recentCount + 1), { expirationTtl: 60 });

  // Parse email from JSON body
  let email;
  try {
    const body = await request.json();
    email = (body.email || '').trim().toLowerCase();
  } catch {
    return json({ error: 'Invalid request body' }, 400);
  }

  // Validate format
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ error: 'Please enter a valid email address.' }, 400);
  }

  // Block disposable domains
  const blocked = ['mailinator.com', 'tempmail.com', '10minutemail.com', 'guerrillamail.com', 'sharklasers.com', 'yopmail.com'];
  const domain = email.split('@')[1];
  if (blocked.includes(domain)) {
    return json({ error: 'Please use a permanent email address.' }, 400);
  }

  // Check duplicate
  const exists = await env.NEWSLETTER.get('sub:' + email);
  if (exists) {
    return json({ message: 'already_subscribed' });
  }

  // Store
  await env.NEWSLETTER.put('sub:' + email, JSON.stringify({
    email: email,
    subscribed_at: new Date().toISOString(),
    ip: ip,
    lang: (request.headers.get('accept-language') || '').split(',')[0] || '',
  }));

  return json({ message: 'subscribed' });
}

function json(data, status) {
  status = status || 200;
  return new Response(JSON.stringify(data), {
    status: status,
    headers: {
      'content-type': 'application/json',
      'access-control-allow-origin': '*',
      'access-control-allow-methods': 'POST, OPTIONS',
      'access-control-allow-headers': 'Content-Type',
    },
  });
}

// CORS preflight
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
