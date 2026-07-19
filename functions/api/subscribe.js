// Cloudflare Pages Function: Newsletter subscription handler
// POST /api/subscribe → validate → store in KV → send welcome email via Brevo API → JSON response

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

  // Parse email
  let email;
  try {
    const body = await request.json();
    email = (body.email || '').trim().toLowerCase();
  } catch {
    return json({ error: 'Invalid request body' }, 400);
  }

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ error: 'Please enter a valid email address.' }, 400);
  }

  const blocked = ['mailinator.com', 'tempmail.com', '10minutemail.com', 'guerrillamail.com', 'sharklasers.com', 'yopmail.com'];
  if (blocked.includes(email.split('@')[1])) {
    return json({ error: 'Please use a permanent email address.' }, 400);
  }

  // Check duplicate
  const exists = await env.NEWSLETTER.get('sub:' + email);
  if (exists) {
    return json({ message: 'already_subscribed' });
  }

  // Store subscriber
  const subscribedAt = new Date().toISOString();
  await env.NEWSLETTER.put('sub:' + email, JSON.stringify({
    email,
    subscribed_at: subscribedAt,
    ip,
    lang: (request.headers.get('accept-language') || '').split(',')[0] || '',
  }));

  // Send welcome email via Brevo API
  const emailResult = await sendBrevo(email, subscribedAt, env);

  return json({ message: 'subscribed', email_status: emailResult });
}

async function sendBrevo(to, subscribedAt, env) {
  const date = new Date(subscribedAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  const name = to.split('@')[0];
  const subject = 'Welcome to ChinaTripBox';

  const htmlContent = '<p>Welcome to ChinaTripBox!</p>'
    + '<p>Hi ' + escapeHtml(name) + ',</p>'
    + '<p>You\'re subscribed to the ChinaTripBox newsletter. Every week you\'ll get:</p>'
    + '<ul>'
    + '<li>New city guides & travel tips</li>'
    + '<li>Policy changes for foreign visitors</li>'
    + '<li>Tool updates & seasonal advice</li>'
    + '</ul>'
    + '<p>First tip: <a href="https://www.chinatripbox.com/posts/alipay-foreign-credit-card-step-by-step/">Set up Alipay before you fly</a>.</p>'
    + '<p style="color:#888;font-size:12px">Subscribed on ' + escapeHtml(date) + '.<br>'
    + '<a href="https://www.chinatripbox.com/contact/">Unsubscribe</a></p>';

  try {
    const resp = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST',
      headers: {
        'api-key': env.BREVO_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        sender: { name: 'ChinaTripBox', email: 'zh13809022788@gmail.com' },
        to: [{ email: to, name: name }],
        subject: subject,
        htmlContent: htmlContent,
      }),
    });

    if (!resp.ok) {
      const errBody = await resp.text();
      return { ok: false, error: 'Brevo API ' + resp.status + ': ' + errBody };
    }

    return { ok: true, detail: 'sent' };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function json(data, status) {
  status = status || 200;
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
