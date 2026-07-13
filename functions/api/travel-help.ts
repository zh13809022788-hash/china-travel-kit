interface Env {
  DEEPSEEK_API_KEY?: string;
}

interface TravelHelpRequest {
  message?: string;
  stage?: string;
  topic?: string;
  location?: string;
}

const json = (body: unknown, init: ResponseInit = {}) =>
  new Response(JSON.stringify(body), {
    ...init,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      ...init.headers,
    },
  });

const sanitize = (value: unknown, maxLength: number) =>
  String(value ?? '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, maxLength);

export const onRequestOptions = () =>
  new Response(null, {
    status: 204,
    headers: {
      allow: 'POST, OPTIONS',
    },
  });

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  if (!env.DEEPSEEK_API_KEY) {
    return json({ error: 'AI helper is not configured yet.' }, { status: 503 });
  }

  let payload: TravelHelpRequest;
  try {
    payload = await request.json();
  } catch {
    return json({ error: 'Invalid JSON request.' }, { status: 400 });
  }

  const message = sanitize(payload.message, 1800);
  const stage = sanitize(payload.stage, 80) || 'Not specified';
  const topic = sanitize(payload.topic, 80) || 'General trip setup';
  const location = sanitize(payload.location, 160) || 'Not specified';

  if (message.length < 8) {
    return json({ error: 'Please add a more detailed travel question.' }, { status: 400 });
  }

  const systemPrompt = [
    'You are ChinaTripBox Travel Help, a practical assistant for foreign visitors to China.',
    'Give concise, step-by-step travel guidance in English.',
    'Focus on payment apps, eSIM/internet, transport, local apps, arrival setup, cash backup, and simple trip logistics.',
    'Do not ask for passport photos, full bank card numbers, passwords, PINs, one-time codes, or account logins.',
    'Do not provide legal, immigration, medical, banking, emergency, or official government advice.',
    'When a question is high-risk or account-specific, explain what to check with the official provider and suggest human review.',
    'Keep the answer practical, calm, and under 220 words.',
  ].join(' ');

  const userPrompt = [
    `Trip stage: ${stage}`,
    `Topic: ${topic}`,
    `City or route: ${location}`,
    '',
    'Question:',
    message,
  ].join('\n');

  const response = await fetch('https://api.deepseek.com/chat/completions', {
    method: 'POST',
    headers: {
      authorization: `Bearer ${env.DEEPSEEK_API_KEY}`,
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: 'deepseek-chat',
      temperature: 0.3,
      max_tokens: 420,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
    }),
  });

  if (!response.ok) {
    return json(
      { error: 'The AI helper is temporarily unavailable. Please try again later.' },
      { status: 502 },
    );
  }

  const data = (await response.json()) as {
    choices?: Array<{ message?: { content?: string } }>;
  };
  const answer = data.choices?.[0]?.message?.content?.trim();

  if (!answer) {
    return json({ error: 'The AI helper returned an empty answer.' }, { status: 502 });
  }

  return json({
    answer,
    model: 'deepseek-chat',
  });
};
