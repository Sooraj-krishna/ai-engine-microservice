import { applyIncrementalFixes, FixResult, SectionInput } from './incrementalFixer';

export interface IssueInput {
  id: string;
  title: string;
  description: string;
  files: Array<{
    path: string;
    sections: Array<{
      name: string;
      code: string;
      language?: string;
    }>;
  }>;
}

export interface IssueFixOptions {
  minContext?: number;
  maxRetries?: number;
  validate?: (original: string, fix: string) => boolean;
  log?: (line: string) => void;
}

export interface IssueFixReport {
  issueId: string;
  summary: {
    total: number;
    success: number;
    failed: number;
    skipped: number;
  };
  results: FixResult[];
}

const defaultLog = (line: string) => console.log(line); // eslint-disable-line no-console

/**
 * Process an issue by fixing its sections one-by-one using incremental fixes.
 * Caller supplies the issue->files->sections mapping to keep context small.
 */
export async function processIssue(
  issue: IssueInput,
  options: IssueFixOptions = {}
): Promise<IssueFixReport> {
  const log = options.log ?? defaultLog;

  // Flatten sections with file/section metadata for the incremental fixer
  const sections: SectionInput[] = issue.files.flatMap((file) =>
    file.sections.map((section) => ({
      file: file.path,
      section: section.name,
      code: section.code,
      language: section.language,
    }))
  );

  log(`[ISSUE] Processing issue ${issue.id}: ${issue.title}`);
  const results = await applyIncrementalFixes(sections, {
    minContext: options.minContext,
    maxRetries: options.maxRetries,
    validate: options.validate,
  });

  const summary = results.reduce(
    (acc, r) => {
      acc.total += 1;
      acc[r.status] += 1;
      return acc;
    },
    { total: 0, success: 0, failed: 0, skipped: 0 } as IssueFixReport['summary']
  );

  // Log outcomes
  for (const r of results) {
    const base = `[ISSUE ${issue.id}] ${r.status.toUpperCase()} :: ${r.file} :: ${r.section}`;
    const reason = r.reason ? ` | reason: ${r.reason}` : '';
    const model = r.model_used ? ` | model: ${r.model_used}` : '';
    log(base + model + reason);
  }

  log(
    `[ISSUE ${issue.id}] Summary: total=${summary.total} success=${summary.success} skipped=${summary.skipped} failed=${summary.failed}`
  );

  return {
    issueId: issue.id,
    summary,
    results,
  };
}

