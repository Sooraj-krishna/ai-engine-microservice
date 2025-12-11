import { NextResponse } from 'next/server';
import { ask } from '@/lib/modelRouter';

export const runtime = 'nodejs'; // ensure server runtime

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { messages, minContext } = body ?? {};
    if (!Array.isArray(messages)) {
      return NextResponse.json({ error: 'messages must be an array' }, { status: 400 });
    }

    const result = await ask({ messages, minContext });
    return NextResponse.json(result);
  } catch (error: any) {
    return NextResponse.json({ error: error?.message ?? 'Unknown error' }, { status: 500 });
  }
}

