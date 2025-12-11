/**
 * Dynamic model selection and fallback for OpenRouter.
 * - Fetches available models
 * - Prioritizes free/efficient coding models
 * - Respects context length needs
 * - Retries with fallbacks on rate limits, context errors, or provider errors
 */

import { setTimeout as delay } from 'timers/promises';

export type ChatMessage = { role: 'system' | 'user' | 'assistant'; content: string };

export interface AskParams {
  messages: ChatMessage[];
  minContext?: number;
  preferredModels?: string[];
  enableFreeFallback?: boolean;
  forceFreeOnly?: boolean;
  timeoutMs?: number;
  maxRetries?: number;
}

export interface AskResult {
  model_used: string;
  fallbacks_attempted: string[];
  content: string;
  raw_response: unknown;
}

interface ModelInfo {
  id: string;
  context_length: number;
  is_free: boolean;
  raw: any; // eslint-disable-line @typescript-eslint/no-explicit-any
}

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
const OPENROUTER_BASE_URL = process.env.OPENROUTER_BASE_URL ?? 'https://openrouter.ai/api/v1';
const OPENROUTER_REFERRER = process.env.OPENROUTER_REFERRER ?? 'http://localhost';
const OPENROUTER_TITLE = process.env.OPENROUTER_TITLE ?? 'AI Engine Microservice';

const DEFAULT_PREFERRED_MODELS: string[] = [
  // Strong coding/reasoning, large context (often free-tier)
  'deepseek/deepseek-reasoner',
  'deepseek/deepseek-chat',
  'qwen/qwen-2-72b-instruct',
  'qwen/qwen-2-7b-instruct',
  // Mixture-of-experts and coding-tuned options
  'mistralai/mixtral-8x7b-instruct',
  'mistralai/mistral-7b-instruct',
  'nousresearch/nous-hermes-2-mixtral-8x7b-sft',
  'openchat/openchat-7b',
  // Additional free/low-cost coding-friendly models
  'snowflake/snowflake-arctic-instruct',
  'meta-llama/llama-3-8b-instruct',
  'meta-llama/llama-3-70b-instruct',
  'tiiuae/falcon-180b-chat',
];

const DEFAULT_ENABLE_FREE_FALLBACK = (process.env.OPENROUTER_ENABLE_FREE_FALLBACK ?? 'true').toLowerCase() === 'true';
const DEFAULT_FORCE_FREE_ONLY = (process.env.OPENROUTER_FORCE_FREE_ONLY ?? 'true').toLowerCase() === 'true';
const DEFAULT_TIMEOUT_MS = 60_000;
const DEFAULT_MAX_RETRIES = 6;

async function fetchAvailableModels(): Promise<Record<string, ModelInfo>> {
  if (!OPENROUTER_API_KEY) return {};

  try {
    const resp = await fetch(`${OPENROUTER_BASE_URL}/models`, {
      headers: { Authorization: `Bearer ${OPENROUTER_API_KEY}` },
      // 15s timeout guard
      signal: AbortSignal.timeout(15_000),
    });
    if (!resp.ok) {
      console.warn('[modelRouter] Failed to fetch models', resp.status, await resp.text());
      return {};
    }
    const data = await resp.json();
    const models = data?.data ?? data?.models ?? [];
    const map: Record<string, ModelInfo> = {};
    for (const m of models) {
      const id = m?.id;
      if (!id) continue;
      const pricing = m?.pricing ?? {};
      const promptCost = pricing.prompt ?? pricing.input ?? null;
      const isFree = promptCost === 0;
      const contextLength = m?.context_length ?? m?.max_context_length ?? 0;
      map[id] = { id, context_length: contextLength, is_free: Boolean(isFree), raw: m };
    }
    return map;
  } catch (err) {
    console.warn('[modelRouter] Error fetching models', err);
    return {};
  }
}

function shouldRetry(status: number, body: string): boolean {
  if ([429, 500, 502, 503, 504].includes(status)) return true;
  if (body.includes('context_length') || body.includes('context_length_exceeded')) return true;
  if (body.includes('model_not_available') || body.includes('provider_error')) return true;
  return false;
}

function selectCandidates(opts: {
  available: Record<string, ModelInfo>;
  minContext: number;
  preferred: string[];
  enableFreeFallback: boolean;
  forceFreeOnly: boolean;
}): string[] {
  const { available, minContext, preferred, enableFreeFallback, forceFreeOnly } = opts;
  const candidates: string[] = [];

  const isEligible = (id: string) => {
    const info = available[id];
    if (!info) return false;
    if (forceFreeOnly && !info.is_free) return false;
    return info.context_length >= minContext;
  };

  // Preferred list first
  for (const id of preferred) {
    if (isEligible(id)) candidates.push(id);
  }

  // Free fallbacks
  if (enableFreeFallback) {
    for (const [id, info] of Object.entries(available)) {
      if (candidates.includes(id)) continue;
      if (info.is_free && info.context_length >= minContext) candidates.push(id);
    }
  }

  // Any remaining that satisfy context (if not force-free or already included)
  for (const [id, info] of Object.entries(available)) {
    if (candidates.includes(id)) continue;
    if (info.context_length >= minContext && (!forceFreeOnly || info.is_free)) {
      candidates.push(id);
    }
  }

  return candidates;
}

export async function ask(params: AskParams): Promise<AskResult> {
  if (!OPENROUTER_API_KEY) throw new Error('OpenRouter API key not configured');

  const {
    messages,
    minContext = 8_000,
    preferredModels = DEFAULT_PREFERRED_MODELS,
    enableFreeFallback = DEFAULT_ENABLE_FREE_FALLBACK,
    forceFreeOnly = DEFAULT_FORCE_FREE_ONLY,
    timeoutMs = DEFAULT_TIMEOUT_MS,
    maxRetries = DEFAULT_MAX_RETRIES,
  } = params;

  const available = await fetchAvailableModels();
  const candidates = selectCandidates({
    available,
    minContext,
    preferred: preferredModels,
    enableFreeFallback,
    forceFreeOnly,
  });

  if (!candidates.length) {
    throw new Error('No models satisfy context/availability constraints');
  }

  const tried: string[] = [];
  let lastError: unknown = null;

  for (const model of candidates.slice(0, maxRetries)) {
    tried.push(model);
    try {
      const body = {
        model,
        messages,
        temperature: 0.1,
        top_p: 0.8,
        max_tokens: 2000,
      };

      const resp = await fetch(`${OPENROUTER_BASE_URL}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${OPENROUTER_API_KEY}`,
          'HTTP-Referer': OPENROUTER_REFERRER,
          'X-Title': OPENROUTER_TITLE,
        },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(timeoutMs),
      });

      const text = await resp.text();
      if (resp.ok) {
        const data = JSON.parse(text);
        const content = data?.choices?.[0]?.message?.content ?? '';
        return {
          model_used: model,
          fallbacks_attempted: tried,
          content,
          raw_response: data,
        };
      }

      if (shouldRetry(resp.status, text)) {
        lastError = new Error(`Retryable error ${resp.status}: ${text}`);
        await delay(750);
        continue;
      }

      lastError = new Error(`Non-retryable error ${resp.status}: ${text}`);
      break;
    } catch (err) {
      lastError = err;
      await delay(750);
      continue;
    }
  }

  const err = lastError instanceof Error ? lastError.message : String(lastError);
  throw new Error(`All model attempts failed. Tried: ${tried.join(', ')}. Last error: ${err}`);
}

