/**
 * Gemini API router for code generation.
 * Uses Gemini as the primary and only AI API.
 */

export type ChatMessage = { role: 'system' | 'user' | 'assistant'; content: string };

export interface AskParams {
  messages: ChatMessage[];
  minContext?: number;
  timeoutMs?: number;
}

export interface AskResult {
  model_used: string;
  fallbacks_attempted: string[];
  content: string;
  raw_response: unknown;
}

const DEFAULT_TIMEOUT_MS = 60_000;

/**
 * Query Gemini API via backend endpoint
 */
async function queryGeminiViaBackend(
  messages: ChatMessage[],
  model?: string,
  timeoutMs?: number
): Promise<AskResult> {
  try {
    const resp = await fetch('/api/gemini', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, model, timeoutMs }),
      signal: AbortSignal.timeout(timeoutMs ?? DEFAULT_TIMEOUT_MS),
    });

    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`Gemini API error ${resp.status}: ${text}`);
    }

    const data = await resp.json();
    return {
      model_used: data.model_used ?? 'gemini:unknown',
      fallbacks_attempted: data.fallbacks_attempted ?? [],
      content: data.content ?? '',
      raw_response: data.raw_response ?? {},
    };
  } catch (err) {
    throw new Error(`Gemini API call failed: ${err instanceof Error ? err.message : String(err)}`);
  }
}

/**
 * Query Gemini API for code generation.
 * Uses Gemini Pro for large contexts (100k+ tokens), Flash otherwise.
 */
export async function ask(params: AskParams): Promise<AskResult> {
  const { messages, minContext = 8000, timeoutMs = DEFAULT_TIMEOUT_MS } = params;

  // Use Pro model for very large contexts, Flash for normal
  const geminiModel = minContext >= 100000 ? 'gemini-1.5-pro-latest' : 'gemini-1.5-flash-latest';
  console.log(`[modelRouter] Using Gemini (${geminiModel}) for context: ${minContext} tokens`);

  return await queryGeminiViaBackend(messages, geminiModel, timeoutMs);
}
