#!/usr/bin/env python3
"""Verify Chinese-language citations for authenticity and completeness.

Checks citation format, DOI resolveability, and structural integrity for
中文参考文献 (Chinese-language references). Produces a structured report
flagging SUSPICIOUS / INCOMPLETE / FAKE citations.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from _paper_spine_utils import markdown_tables, table_rows

USER_AGENT = "PaperSpine/3.0 (citation-zh; https://github.com/WUBING2023/PaperSpine)"
DOI_RE = re.compile(r"(?:doi\s*[:=]\s*|https?://doi\.org/)?(10\.\d{4,}/[^\s,;)]+)", re.IGNORECASE)

# Chinese citation format patterns
CN_AUTHOR_RE = re.compile(r"[^\x00-\x7f]{2,4}(?:[,，、\s]+[^\x00-\x7f]{2,4})*")  # Chinese author names
CN_JOURNAL_RE = re.compile(r"《([^》]+)》")  # 《期刊名》
CN_YEAR_RE = re.compile(r"(\d{4})[年]?")
CN_VOLUME_RE = re.compile(r"(\d+)\s*[卷\(（]")
CN_PAGES_RE = re.compile(r"(\d+)[-~]\s*(\d+)")

@dataclass
class CitationCheckZH:
    candidate_id: str
    reference_text: str
    status: str  # VERIFIED / SUSPICIOUS / INCOMPLETE / FAKE
    has_author: bool = False
    has_title: bool = False
    has_journal: bool = False
    has_year: bool = False
    has_doi: bool = False
    doi_resolves: bool = False
    issues: list[str] = field(default_factory=list)


@dataclass
class CitationVerificationZHResult:
    path: str
    total: int = 0
    verified: int = 0
    suspicious: int = 0
    incomplete: int = 0
    fake: int = 0
    checks: list[CitationCheckZH] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.fake == 0 and self.suspicious == 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Chinese citations for PaperSpine.")
    parser.add_argument("output_dir", nargs="?", default="paper_rewriting_output")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def check_zh_format(ref: str) -> dict:
    return {
        "has_author": bool(CN_AUTHOR_RE.search(ref)),
        "has_journal": bool(CN_JOURNAL_RE.search(ref)),
        "has_year": bool(CN_YEAR_RE.search(ref)),
    }


def has_doi(ref: str) -> str:
    m = DOI_RE.search(ref)
    return m.group(1) if m else ""


def verify_doi(doi: str) -> bool:
    try:
        req = Request(f"https://api.crossref.org/works/{doi}", headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception:
        return False


def check_citation_bank_zh(out_dir: Path) -> CitationVerificationZHResult:
    bank_path = out_dir / "citation_support_bank.md"
    if not bank_path.exists():
        return CitationVerificationZHResult(str(bank_path))

    text = bank_path.read_text(encoding="utf-8", errors="ignore")
    _, rows = table_rows(text)
    if not rows:
        return CitationVerificationZHResult(str(bank_path))

    result = CitationVerificationZHResult(str(bank_path), total=len(rows))

    for row in rows:
        joined = " ".join(row)
        candidate_id = row[0] if len(row) > 0 else "?"
        ref = row[1] if len(row) > 1 else joined

        check = CitationCheckZH(candidate_id=candidate_id, reference_text=ref[:120])

        fmt = check_zh_format(ref)
        check.has_author = fmt["has_author"]
        check.has_journal = fmt["has_journal"]
        check.has_year = fmt["has_year"]

        # Check for obvious fabrications
        if len(ref.strip()) < 20:
            check.status = "FAKE"
            check.issues.append("Citation text too short — likely fabricated")

        elif not check.has_author and not check.has_journal:
            check.status = "FAKE"
            check.issues.append("No author or journal found — likely fabricated")

        elif not check.has_author or not check.has_journal or not check.has_year:
            check.status = "INCOMPLETE"
            missing = []
            if not check.has_author: missing.append("author")
            if not check.has_journal: missing.append("journal")
            if not check.has_year: missing.append("year")
            check.issues.append(f"Missing: {', '.join(missing)}")

        else:
            doi = has_doi(ref)
            check.has_doi = bool(doi)
            if doi:
                time.sleep(0.3)
                check.doi_resolves = verify_doi(doi)
                if not check.doi_resolves:
                    check.status = "SUSPICIOUS"
                    check.issues.append(f"DOI {doi[:30]} does not resolve")
                else:
                    check.status = "VERIFIED"
            else:
                check.status = "SUSPICIOUS"
                check.issues.append("No DOI — cannot verify authenticity. Add DOI or verify manually")

        if check.status == "VERIFIED": result.verified += 1
        elif check.status == "SUSPICIOUS": result.suspicious += 1
        elif check.status == "INCOMPLETE": result.incomplete += 1
        elif check.status == "FAKE": result.fake += 1
        result.checks.append(check)

    return result


def to_markdown(result: CitationVerificationZHResult) -> str:
    lines = [
        "# Chinese Citation Verification Report",
        "",
        f"- Total citations: {result.total}",
        f"- Verified: {result.verified}",
        f"- Suspicious: {result.suspicious}",
        f"- Incomplete: {result.incomplete}",
        f"- Likely fake: {result.fake}",
        f"- Status: {'PASS' if result.ok else 'FAIL'}",
        "",
        "## Details",
        "",
        "| ID | Reference | Status | Issues |",
        "|---|---|---|---|",
    ]
    for c in result.checks:
        lines.append(f"| {c.candidate_id} | {c.reference_text[:60]} | {c.status} | {'; '.join(c.issues[:2])} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    result = check_citation_bank_zh(out_dir)

    if args.json:
        print(json.dumps({"ok": result.ok, "total": result.total, "verified": result.verified, "suspicious": result.suspicious, "incomplete": result.incomplete, "fake": result.fake}, ensure_ascii=False, indent=2))
    if args.markdown or not args.json:
        print(to_markdown(result))

    if args.write:
        (out_dir / "citation_verification_zh.md").write_text(to_markdown(result), encoding="utf-8")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
