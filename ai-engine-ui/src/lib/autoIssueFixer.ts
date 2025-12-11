import fs from 'fs/promises';
import path from 'path';
import { processIssue, IssueInput, IssueFixOptions, IssueFixReport } from './issueFixer';

export interface AutoIssueConfig {
  id: string;
  title: string;
  description: string;
  /**
   * Glob-like substrings or regex sources to include (evaluated as RegExp).
   * Example: ['src/utils', '\\.tsx$']
   */
  pathPatterns: string[];
  /**
   * Optional extensions to include (e.g., ['.ts', '.tsx', '.js']).
   * If empty, all files passing pathPatterns are considered.
   */
  extensions?: string[];
  /**
   * Maximum files to process to keep context bounded.
   */
  maxFiles?: number;
}

const DEFAULT_IGNORES = ['node_modules', '.git', '.next', '.turbo', 'dist', 'build', '.cache'];

function matchPatterns(filePath: string, patterns: string[]): boolean {
  if (!patterns.length) return true;
  return patterns.every((p) => {
    const re = new RegExp(p);
    return re.test(filePath);
  });
}

function matchExtension(filePath: string, exts?: string[]): boolean {
  if (!exts || !exts.length) return true;
  return exts.includes(path.extname(filePath));
}

async function* walk(dir: string): AsyncGenerator<string> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (DEFAULT_IGNORES.includes(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      yield* walk(full);
    } else if (entry.isFile()) {
      yield full;
    }
  }
}

export async function autoProcessIssue(
  cfg: AutoIssueConfig,
  options: IssueFixOptions = {}
): Promise<IssueFixReport> {
  const root = process.cwd();
  const matchedFiles: { path: string; content: string }[] = [];

  for await (const filePath of walk(root)) {
    const rel = path.relative(root, filePath);
    if (!matchExtension(rel, cfg.extensions)) continue;
    if (!matchPatterns(rel, cfg.pathPatterns)) continue;
    matchedFiles.push({ path: rel, content: await fs.readFile(filePath, 'utf8') });
    if (cfg.maxFiles && matchedFiles.length >= cfg.maxFiles) break;
  }

  const issue: IssueInput = {
    id: cfg.id,
    title: cfg.title,
    description: cfg.description,
    files: matchedFiles.map((f) => ({
      path: f.path,
      sections: [
        {
          name: 'whole-file',
          code: f.content,
          language: inferLanguage(f.path),
        },
      ],
    })),
  };

  if (!issue.files.length) {
    return {
      issueId: cfg.id,
      summary: { total: 0, success: 0, failed: 0, skipped: 0 },
      results: [],
    };
  }

  return processIssue(issue, options);
}

function inferLanguage(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === '.ts' || ext === '.tsx') return 'TypeScript';
  if (ext === '.js' || ext === '.jsx') return 'JavaScript';
  if (ext === '.py') return 'Python';
  if (ext === '.md') return 'Markdown';
  return 'Text';
}

