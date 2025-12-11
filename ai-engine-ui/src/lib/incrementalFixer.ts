/**
 * Incremental fix pipeline:
 * - Processes files/sections one at a time
 * - Uses dynamic model selection (ask) for code generation
 * - Retries on transient model failures
 * - Validates fixes before applying
 * - Produces structured results and logs
 */

import { ask, ChatMessage } from './modelRouter';

export type FixStatus = 'success' | 'skipped' | 'failed';

export interface SectionInput {
  file: string;
  section: string;
  code: string;
  language?: string;
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
  validate?: (original: string, fix: string) => boolean;
}

const DEFAULT_VALIDATE = (original: string, fix: string) => {
  if (!fix || fix.trim().length === 0) return false;
  // reject if fix deletes everything
  if (fix.trim().length < original.trim().length * 0.1) return false;
  return true;
};

const buildPrompt = (input: SectionInput): ChatMessage[] => {
  const lang = input.language ?? 'JavaScript';
  return [
    {
      role: 'system',
      content:
        'You are a senior software engineer. Provide minimal, safe fixes. Return only the fixed code. Do not add explanations.',
    },
    {
      role: 'user',
      content: `File: ${input.file}
Section: ${input.section}
Language: ${lang}

Existing code:
${input.code}

Goal: Fix issues, keep behavior non-breaking, preserve exports, and keep changes minimal.`,
    },
  ];
};

export async function applyIncrementalFixes(
  sections: SectionInput[],
  options: ApplyOptions = {}
): Promise<FixResult[]> {
  const results: FixResult[] = [];
  const validate = options.validate ?? DEFAULT_VALIDATE;
  const minContext = options.minContext ?? 8000;
  const maxRetries = options.maxRetries ?? 3;

  for (const section of sections) {
    const resultBase: FixResult = {
      file: section.file,
      section: section.section,
      fix: '',
      status: 'failed',
    };

    try {
      let attempt = 0;
      let lastErr: unknown = null;
      while (attempt < maxRetries) {
        attempt += 1;
        try {
          const messages = buildPrompt(section);
          const response = await ask({
            messages,
            minContext,
          });

          const code = (response.content ?? '').trim();
          if (!validate(section.code, code)) {
            resultBase.status = 'skipped';
            resultBase.reason = 'Validation rejected fix (empty or too destructive)';
            resultBase.fix = code;
            resultBase.model_used = response.model_used;
            resultBase.fallbacks_attempted = response.fallbacks_attempted;
            break;
          }

          // Apply: Here we simply return the fixed snippet; integration can patch files.
          resultBase.fix = code;
          resultBase.status = 'success';
          resultBase.model_used = response.model_used;
          resultBase.fallbacks_attempted = response.fallbacks_attempted;
          logFix({
            ...resultBase,
            status: 'success',
          });
          break;
        } catch (err) {
          lastErr = err;
          if (attempt >= maxRetries) {
            throw err;
          }
        }
      }

      if (resultBase.status === 'failed' && lastErr) {
        resultBase.reason = lastErr instanceof Error ? lastErr.message : String(lastErr);
      }
      if (resultBase.status === 'failed') {
        logFix({ ...resultBase, status: 'failed' });
      }
    } catch (err) {
      resultBase.status = 'failed';
      resultBase.reason = err instanceof Error ? err.message : String(err);
      logFix(resultBase);
    }

    results.push(resultBase);
  }

  return results;
}

export function logFix(result: FixResult) {
  const base = `[FIX][${result.status.toUpperCase()}] ${result.file} :: ${result.section}`;
  const reason = result.reason ? ` | reason: ${result.reason}` : '';
  const model = result.model_used ? ` | model: ${result.model_used}` : '';
  // eslint-disable-next-line no-console
  console.log(base + model + reason);
}

