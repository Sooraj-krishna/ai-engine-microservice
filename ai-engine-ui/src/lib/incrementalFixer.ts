/**
 * Incremental Fixer for Web/JS/TS projects
 * - Splits large code sections into token-sized chunks
 * - Calls Gemini API with adaptive minContext
 * - Validates fixes before returning
 * - Logs structured results
 */

import { ask, ChatMessage } from './modelRouter';

export type FixStatus = 'success' | 'skipped' | 'failed';

export interface SectionInput {
  file: string;
  section: string;
  code: string;
  language?: string;
  issueDescription?: string;
  locationHint?: string;
}

export interface FixResult {
  file: string;
  section: string;
  fix: string;
  status: FixStatus;
  reason?: string;
  model_used?: string;
  fallbacks_attempted?: string[];
}

interface ApplyOptions {
  minContext?: number;
  maxRetries?: number;
  maxTokensPerChunk?: number; // New: max tokens per chunk
  validate?: (original: string, fix: string) => boolean;
}

const DEFAULT_VALIDATE = (original: string, fix: string) => {
  if (!fix || fix.trim().length === 0) return false;
  if (fix.trim().length < original.trim().length * 0.1) return false;
  return true;
};

/**
 * Split code section into chunks based on token estimate
 */
function splitCodeIntoChunks(
  section: SectionInput,
  maxTokensPerChunk: number = 2000
): SectionInput[] {
  const lines = section.code.split('\n');
  const chunks: SectionInput[] = [];
  let currentChunk: string[] = [];
  let currentTokens = 0;
  let chunkIndex = 1;

  for (const line of lines) {
    const approxTokens = Math.ceil(line.length / 4); // rough token estimate
    if (currentTokens + approxTokens > maxTokensPerChunk && currentChunk.length > 0) {
      chunks.push({
        ...section,
        section: `${section.section}_chunk${chunkIndex}`,
        code: currentChunk.join('\n'),
      });
      currentChunk = [];
      currentTokens = 0;
      chunkIndex++;
    }
    currentChunk.push(line);
    currentTokens += approxTokens;
  }

  if (currentChunk.length > 0) {
    chunks.push({
      ...section,
      section: `${section.section}_chunk${chunkIndex}`,
      code: currentChunk.join('\n'),
    });
  }

  return chunks;
}

/**
 * Build system/user messages for Gemini API
 */
const buildPrompt = (input: SectionInput): ChatMessage[] => {
  const lang = input.language ?? 'JavaScript';
  const issue = input.issueDescription ? `Issue: ${input.issueDescription}\n` : '';
  const location = input.locationHint ? `Location: ${input.locationHint}\n` : '';
  return [
    {
      role: 'system',
      content:
        'You are a senior software engineer. Provide minimal, safe fixes. Return only the fixed code. Do not add explanations.',
    },
    {
      role: 'user',
      content: `${issue}${location}File: ${input.file}
Section: ${input.section}
Language: ${lang}

Existing code:
${input.code}

Goal: Fix the described issue, keep behavior non-breaking, preserve exports, and keep changes minimal.`,
    },
  ];
};

/**
 * Apply incremental fixes on multiple sections
 */
export async function applyIncrementalFixes(
  sections: SectionInput[],
  options: ApplyOptions = {}
): Promise<FixResult[]> {
  const results: FixResult[] = [];
  const validate = options.validate ?? DEFAULT_VALIDATE;
  const minContext = options.minContext ?? 2000;
  const maxRetries = options.maxRetries ?? 3;
  const maxTokensPerChunk = options.maxTokensPerChunk ?? 2000;

  for (const section of sections) {
    // Split large section into chunks
    const chunks = splitCodeIntoChunks(section, maxTokensPerChunk);

    for (const chunk of chunks) {
      const resultBase: FixResult = {
        file: chunk.file,
        section: chunk.section,
        fix: '',
        status: 'failed',
      };

      try {
        let attempt = 0;
        let lastErr: unknown = null;

        while (attempt < maxRetries) {
          attempt++;
          try {
            const messages = buildPrompt(chunk);
            const response = await ask({
              messages,
              minContext,
            });

            const code = (response.content ?? '').trim();
            if (!validate(chunk.code, code)) {
              resultBase.status = 'skipped';
              resultBase.reason = 'Validation rejected fix (empty or too destructive)';
              resultBase.fix = code;
              resultBase.model_used = response.model_used;
              resultBase.fallbacks_attempted = response.fallbacks_attempted;
              break;
            }

            resultBase.fix = code;
            resultBase.status = 'success';
            resultBase.model_used = response.model_used;
            resultBase.fallbacks_attempted = response.fallbacks_attempted;
            logFix(resultBase);
            break;
          } catch (err) {
            lastErr = err;
            if (attempt >= maxRetries) break;
          }
        }

        if (resultBase.status === 'failed' && lastErr) {
          resultBase.reason = lastErr instanceof Error ? lastErr.message : String(lastErr);
        }

        if (resultBase.status === 'failed') logFix(resultBase);
      } catch (err) {
        resultBase.status = 'failed';
        resultBase.reason = err instanceof Error ? err.message : String(err);
        logFix(resultBase);
      }

      results.push(resultBase);
    }
  }

  return results;
}

/**
 * Log the fix attempt
 */
export function logFix(result: FixResult) {
  const base = `[FIX][${result.status.toUpperCase()}] ${result.file} :: ${result.section}`;
  const reason = result.reason ? ` | reason: ${result.reason}` : '';
  const model = result.model_used ? ` | model: ${result.model_used}` : '';
  console.log(base + model + reason);
}
