import { NextResponse } from 'next/server';

export const runtime = 'nodejs';

/**
 * Proxy endpoint to call Python backend's Gemini API
 * The Python backend handles Gemini directly via google-generativeai
 */
export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { messages, model, timeoutMs } = body ?? {};

    if (!Array.isArray(messages)) {
      return NextResponse.json({ error: 'messages must be an array' }, { status: 400 });
    }

    // Call Python backend's Gemini endpoint
    const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000';
    const resp = await fetch(`${backendUrl}/api/gemini`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, model, timeoutMs }),
      signal: AbortSignal.timeout(timeoutMs ?? 60_000),
    });

    if (!resp.ok) {
      const text = await resp.text();
      return NextResponse.json({ error: `Backend error: ${text}` }, { status: resp.status });
    }

    const data = await resp.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error?.message ?? 'Unknown error' },
      { status: 500 }
    );
  }
}

