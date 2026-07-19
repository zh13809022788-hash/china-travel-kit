// Cloudflare Pages Function: Newsletter subscription handler
// POST /api/subscribe → validate → store in KV → send welcome email → JSON response
// Email sending via MailChannels (free, no account needed, pre-approved by SPF record)

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

  // Store subscriber
  const subscribedAt = new Date().toISOString();
  await env.NEWSLETTER.put('sub:' + email, JSON.stringify({
    email: email,
    subscribed_at: subscribedAt,
    ip: ip,
    lang: (request.headers.get('accept-language') || '').split(',')[0] || '',
  }));

  // Send welcome email (non-blocking - don't wait for it)
  context.waitUntil(sendWelcomeEmail(email, subscribedAt));

  return json({ message: 'subscribed' });
}

async function sendWelcomeEmail(email, subscribedAt) {
  const url = 'https://api.mailchannels.net/tx/v1/send';
  const payload = {
    personalizations: [{ to: [{ email: email }] }],
    from: { email: 'newsletter@chinatripbox.com', name: 'ChinaTripBox' },
    reply_to: { email: 'contact@chinatripbox.com', name: 'ChinaTripBox' },
    subject: 'Welcome to ChinaTripBox — your first travel tip inside',
    content: [{
      type: 'text/html',
      value: welcomeHtml(email, subscribedAt),
    }],
  };

  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await resp.text();
    console.log('MailChannels response:', resp.status, result);
  } catch (err) {
    console.error('Failed to send welcome email:', err.message);
  }
}

function welcomeHtml(email, subscribedAt) {
  const date = new Date(subscribedAt).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  });
  return `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0;padding:0;background:#faf9f7">
  <table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:40px auto;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #e8e4dd">
    <tr>
      <td style="padding:32px 32px 24px;background:linear-gradient(135deg,#faf9f7,#eeedfe);text-align:center">
        <span style="background:#534AB7;color:#fff;font-size:20px;font-weight:700;width:48px;height:48px;display:inline-flex;align-items:center;justify-content:center;border-radius:12px">CT</span>
        <p style="font-size:20px;font-weight:700;color:#2C2C2A;margin:16px 0 0">Welcome to ChinaTripBox</p>
        <p style="font-size:14px;color:#5F5E5A;margin:8px 0 0">Your weekly China travel tips start now.</p>
      </td>
    </tr>
    <tr>
      <td style="padding:24px 32px 32px">
        <p style="font-size:15px;color:#2C2C2A;line-height:1.7;margin:0">
          Hi ${email.split('@')[0]},
        </p>
        <p style="font-size:15px;color:#2C2C2A;line-height:1.7;margin:16px 0 0">
          You're subscribed to the ChinaTripBox newsletter. Every week you'll get:
        </p>
        <p style="font-size:14px;color:#5F5E5A;line-height:1.8;margin:16px 0 0">
          <span style="color:#3B6D11;font-weight:600">&#10003;</span> New city guides &amp; travel tips<br>
          <span style="color:#3B6D11;font-weight:600">&#10003;</span> Policy changes that affect foreign visitors<br>
          <span style="color:#3B6D11;font-weight:600">&#10003;</span> Tool updates &amp; seasonal travel advice
        </p>

        <div style="background:#f8f6f0;border-radius:8px;padding:16px;margin:24px 0 0">
          <p style="font-size:14px;font-weight:600;color:#2C2C2A;margin:0">Your first tip</p>
          <p style="font-size:13px;color:#5F5E5A;line-height:1.6;margin:8px 0 0">
            Set up <strong>Alipay before you fly</strong>. It takes 10 minutes and works with foreign Visa/Mastercard &mdash; and it's the key to paying for everything in China without hassle.
          </p>
          <a href="https://www.chinatripbox.com/posts/alipay-foreign-credit-card-step-by-step/" style="display:inline-block;margin:12px 0 0;font-size:13px;color:#534AB7;font-weight:600;text-decoration:none">Read: Set up Alipay for foreigners &#8594;</a>
        </div>

        <p style="font-size:13px;color:#888780;margin:24px 0 0;line-height:1.6">
          Subscribed on ${date}. Not your cup of tea?
          <a href="https://www.chinatripbox.com/contact/" style="color:#534AB7">Unsubscribe anytime</a> &mdash; one click, no hard feelings.
        </p>
      </td>
    </tr>
    <tr>
      <td style="border-top:1px solid #e8e4dd;padding:16px 32px;text-align:center">
        <p style="font-size:11px;color:#b4b2a9;margin:0">ChinaTripBox &middot; Independent China travel guides</p>
      </td>
    </tr>
  </table>
</body>
</html>`;
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
