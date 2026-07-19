// Cloudflare Pages Function: Newsletter subscription handler
// POST /api/subscribe → validate → store in KV → send welcome email via Gmail SMTP → JSON response

import { connect } from 'cloudflare:connect';

const GMAIL_USER = 'zh13809022788@gmail.com';
const GMAIL_PASS = 'fhncstamtfwgchww';

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

  // Send welcome email via Gmail SMTP
  const emailResult = await sendGmail(email, subscribedAt);

  return json({ message: 'subscribed', email_status: emailResult });
}

async function sendGmail(to, subscribedAt) {
  const date = new Date(subscribedAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  const name = to.split('@')[0];
  const subject = 'Welcome to ChinaTripBox';

  const body = 'From: ChinaTripBox <' + GMAIL_USER + '>\r\n'
    + 'To: ' + name + ' <' + to + '>\r\n'
    + 'Subject: ' + subject + '\r\n'
    + 'MIME-Version: 1.0\r\n'
    + 'Content-Type: text/plain; charset="UTF-8"\r\n'
    + '\r\n'
    + 'Welcome to ChinaTripBox!\r\n'
    + '\r\n'
    + 'Hi ' + name + ',\r\n'
    + '\r\n'
    + "You're subscribed to the ChinaTripBox newsletter. Every week you'll get:\r\n"
    + '- New city guides & travel tips\r\n'
    + '- Policy changes for foreign visitors\r\n'
    + '- Tool updates & seasonal advice\r\n'
    + '\r\n'
    + 'First tip: Set up Alipay before you fly.\r\n'
    + 'https://www.chinatripbox.com/posts/alipay-foreign-credit-card-step-by-step/\r\n'
    + '\r\n'
    + 'Subscribed on ' + date + '.\r\n'
    + 'Unsubscribe: https://www.chinatripbox.com/contact/\r\n';

  try {
    const result = await smtpSend(to, subject, body);
    return { ok: true, detail: result };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

async function smtpSend(to, subject, body) {
  const socket = await connect({
    host: 'smtp.gmail.com',
    port: 587,
    tls: false, // STARTTLS
  });

  const reader = socket.readable.getReader();
  const writer = socket.writable.getWriter();

  async function read() {
    const { value, done } = await reader.read();
    return new TextDecoder().decode(value || new Uint8Array());
  }
  async function write(cmd) {
    await writer.write(new TextEncoder().encode(cmd + '\r\n'));
  }
  async function expect(code) {
    const resp = await read();
    if (!resp.startsWith(String(code))) {
      throw new Error('SMTP ' + code + ' expected, got: ' + resp.trim());
    }
    return resp;
  }

  await expect(220); // SMTP greeting
  await write('EHLO chinatripbox.com');
  await expect(250);
  await write('STARTTLS');
  await expect(220);

  // Upgrade to TLS
  const tlsSocket = await connect({
    host: 'smtp.gmail.com',
    port: 587,
    tls: true,
    allowHalfOpen: true,
  });

  // Re-authenticate after TLS upgrade
  const tlsReader = tlsSocket.readable.getReader();
  const tlsWriter = tlsSocket.writable.getWriter();

  async function tlsRead() {
    const { value, done } = await tlsReader.read();
    return new TextDecoder().decode(value || new Uint8Array());
  }
  async function tlsWrite(cmd) {
    await tlsWriter.write(new TextEncoder().encode(cmd + '\r\n'));
  }
  async function tlsExpect(code) {
    const resp = await tlsRead();
    if (!resp.startsWith(String(code))) {
      throw new Error('SMTP TLS ' + code + ' expected, got: ' + resp.trim());
    }
    return resp;
  }

  await tlsExpect(220); // After STARTTLS upgrade
  await tlsWrite('EHLO chinatripbox.com');
  await tlsExpect(250);
  await tlsWrite('AUTH LOGIN');
  await tlsExpect(334);
  await tlsWrite(btoa(GMAIL_USER));
  await tlsExpect(334);
  await tlsWrite(btoa(GMAIL_PASS));
  await tlsExpect(235);
  await tlsWrite('MAIL FROM:<' + GMAIL_USER + '>');
  await tlsExpect(250);
  await tlsWrite('RCPT TO:<' + to + '>');
  await tlsExpect(250);
  await tlsWrite('DATA');
  await tlsExpect(354);
  await tlsWrite(body);
  await tlsWrite('.');
  await tlsExpect(250);
  await tlsWrite('QUIT');

  return 'sent';
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
