from collections import deque, Counter
from typing import Deque, Dict, Any
import re

SEVERITY_ORDER = ["error", "warning", "info"]

class LogSummarizer:
    def __init__(self, max_entries: int = 200):
        self.max_entries = max_entries
        self.entries: Deque[Dict[str, str]] = deque(maxlen=max_entries)
        self.counts = Counter()

    def add(self, line: str):
        if not line or not line.strip():
            return
        severity = self._severity(line)
        message = self._normalize(line)
        self.entries.append({"severity": severity, "message": message})
        self.counts[severity] += 1

    def summary(self) -> Dict[str, Any]:
        recent = list(self.entries)[-20:]  # keep small for context size
        top_messages = Counter([e["message"] for e in self.entries]).most_common(10)
        return {
            "counts": {s: self.counts.get(s, 0) for s in SEVERITY_ORDER},
            "recent": recent,
            "top_messages": [{"message": m, "count": c} for m, c in top_messages],
        }

    def _severity(self, line: str) -> str:
        upper = line.upper()
        if "[ERROR]" in upper or "ERROR" in upper or "❌" in upper:
            return "error"
        if "[WARN" in upper or "WARNING" in upper or "⚠" in upper:
            return "warning"
        return "info"

    def _normalize(self, line: str) -> str:
        # Strip timestamps and brackets to keep messages compact
        s = re.sub(r"^\s*\[.*?\]\s*", "", line).strip()
        return s or line.strip()

log_summarizer = LogSummarizer()

