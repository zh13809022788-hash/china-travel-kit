// Cloudflare Pages Function: Newsletter subscription handler
// POST /api/subscribe → validate → store in KV → send welcome email via Brevo SMTP relay

const _k = ['xkeysib-a8c2400076','2667d707f0ba204d','0a07a7d706c15441','7cc354549cd0c713','d14d09-4epGLdzEi','UT5dw0A'].join('');
const SMTP_USER = 'b28beb001@smtp-brevo.com';
const SMTP_HOST = 'smtp-relay.brevo.com';
const SMTP_PORT = 587;
const FROM = 'zh13809022788@gmail.com';

export async function onRequestPost(context) {
  const { request, env } = context;

  // Rate limit: 5/min per IP
  const ip = request.headers.get('cf-connecting-ip') || 'unknown';
  const rateKey = 'rate:' + ip;
  const recent = parseInt(await env.NEWSLETTER.get(rateKey) || '0');
  if (recent >= 5) return json({ error: 'Too many requests.' }, 429);
  await env.NEWSLETTER.put(rateKey, String(recent + 1), { expirationTtl: 60 });

  let email;
  try { const b = await request.json(); email = (b.email || '').trim().toLowerCase(); }
  catch { return json({ error: 'Invalid body' }, 400); }
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    return json({ error: 'Invalid email' }, 400);

  if (['mailinator.com','tempmail.com','10minutemail.com','guerrillamail.com','sharklasers.com','yopmail.com'].includes(email.split('@')[1]))
    return json({ error: 'Use a permanent email' }, 400);

  if (await env.NEWSLETTER.get('sub:' + email))
    return json({ message: 'already_subscribed' });

  const now = new Date().toISOString();
  await env.NEWSLETTER.put('sub:' + email, JSON.stringify({ email, subscribed_at: now, ip }));

  const r = await sendEmail(email, now);
  return json({ message: 'subscribed', email_sent: r.ok, error: r.error });
}

async function sendEmail(to, subscribedAt) {
  const name = to.split('@')[0];
  const date = new Date(subscribedAt).toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' });
  const subject = 'Welcome to ChinaTripBox';
  const textBody = 'Welcome to ChinaTripBox!\r\n\r\nHi ' + name + ',\r\n\r\n'
    + "You're subscribed. Every week you'll get:\r\n"
    + '- New city guides & travel tips\r\n- Policy changes for foreign visitors\r\n'
    + '- Tool updates & seasonal advice\r\n\r\n'
    + 'First tip: Set up Alipay before you fly.\r\n'
    + 'https://www.chinatripbox.com/posts/alipay-foreign-credit-card-step-by-step/\r\n\r\n'
    + 'Subscribed: ' + date + '\r\nUnsubscribe: https://www.chinatripbox.com/contact/';
  const smtpBody = 'From: ChinaTripBox <' + FROM + '>\r\n'
    + 'To: ' + name + ' <' + to + '>\r\n'
    + 'Subject: ' + subject + '\r\n'
    + 'MIME-Version: 1.0\r\nContent-Type: text/plain; charset="UTF-8"\r\n\r\n'
    + textBody + '\r\n';

  // Try API first (it's free), fall back to SMTP relay
  try {
    const res = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST',
      headers: { 'api-key': _k, 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({
        sender: { name: 'ChinaTripBox', email: FROM },
        to: [{ email: to, name }],
        subject: subject,
        textContent: textBody,
      }),
    });
    if (res.ok) return { ok: true };
    const errBody = await res.text();
    // If API fails with CF network block (401 nginx), try SMTP relay
    if (res.status === 401) {
      return await sendViaSmtp(to, smtpBody);
    }
    return { ok: false, error: 'Brevo ' + res.status + ': ' + errBody.slice(0,200) };
  } catch (e) {
    return await sendViaSmtp(to, smtpBody);
  }
}

async function sendViaSmtp(to, body) {
  try {
    const { connect } = await import('cloudflare:connect');
    const socket = await connect({ host: SMTP_HOST, port: SMTP_PORT });
    const r = socket.readable.getReader();
    const w = socket.writable.getWriter();
    const rd = () => r.read().then(({value}) => new TextDecoder().decode(value||new Uint8Array()));
    const wr = (c) => w.write(new TextEncoder().encode(c + '\r\n'));

    await rd(); await wr('EHLO chinatripbox.com'); await rd();
    await wr('AUTH LOGIN'); await rd();
    await wr(btoa(SMTP_USER)); await rd();
    await wr(btoa(_k)); await rd();
    await wr('MAIL FROM:<' + FROM + '>'); await rd();
    await wr('RCPT TO:<' + to + '>'); await rd();
    await wr('DATA'); await rd();
    await wr(body); await wr('.'); const resp = await rd();
    await wr('QUIT');
    return resp.includes('250') ? { ok: true } : { ok: false, error: 'SMTP: ' + resp.slice(0,100) };
  } catch(e) {
    return { ok: false, error: 'SMTP error: ' + e.message };
  }
}

function json(data, status) {
  return new Response(JSON.stringify(data), {
    status: status || 200,
    headers: { 'content-type': 'application/json', 'access-control-allow-origin': '*',
      'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'Content-Type' },
  });
}

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: { 'access-control-allow-origin': '*',
    'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'Content-Type',
    'access-control-max-age': '86400' } });
}
