#!/usr/bin/env python3
"""Export a Markdown, supported LaTeX or Pandoc JSON manuscript through one CSL/citeproc result.

Uses Pandoc's native Figure/Table AST; tested with Pandoc 3.8.3. Other versions
need reference/output checks; 3.12 changed DOCX bookmarks and fails current guards.
PDF export additionally requires a local LaTeX engine.
Adjacent manuscript_refs.lua is a runtime dependency, including in installed scripts.
Layout belongs in --reference-doc/--metadata-file/--template; citation style in --csl.
CLI exit codes: 0 conversion complete with no surface rule matches; 1 conversion
failure; 2 surface or missing-glyph review required; 3 surface extraction incomplete.
Codes 2/3 retain converted files and return their paths in JSON for repair/retry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree
from xml.parsers import expat
from xml.sax.saxutils import escape

# Embedded/isolated Python omits the script directory from sys.path.
_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from latex_guard import check_internal_destinations, check_labels_and_refs  # noqa: E402
from publication_surface_check import to_markdown as surface_markdown  # noqa: E402
from publication_surface_check import validate as validate_surface  # noqa: E402
from word_guard import (  # noqa: E402
    W_NS,
    duplicate_figure_reference_findings,
    inspect_word_figure_geometry,
    internal_reference_findings,
)


def run(command: list[str], cwd: Path, *, input_text: str | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, input=input_text, capture_output=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"{Path(command[0]).name} failed ({result.returncode}):\n{result.stderr or result.stdout[-6000:]}")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if "citation" in result.stderr.lower() and "not found" in result.stderr.lower():
        raise RuntimeError("Unresolved bibliography citation; correct the source/BibTeX key.")
    return result.stdout


def tex_render_diagnostics(log: str, log_path: Path) -> dict:
    """Expose successful TeX builds that silently lost visible characters.

    Inspect only the final compilation log. No findings is not visual approval.
    TeX wraps font names, so preserve bounded continuation lines and the first
    source line for each distinct warning; never replace scientific characters.
    """
    lines = log.splitlines()
    findings = []
    seen = set()
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("Missing character:"):
            continue
        message = line.strip()
        for continuation in lines[index + 1:index + 8]:
            if message.endswith("!"):
                break
            continuation = continuation.strip()
            if not continuation or continuation.startswith((
                "Missing character:", "LaTeX ", "Package ", "Overfull ", "Underfull ", "!",
            )):
                break
            message += " " + continuation
        if message not in seen:
            seen.add(message)
            findings.append({"code": "missing_glyph", "line": index + 1, "message": message})
    return {"status": "review_required" if findings else "no_missing_glyphs",
            "log_path": str(log_path), "findings": findings}


def local_assets(node, source_dir: Path, output: Path) -> None:
    """Keep generated TeX editable/compilable without the source's directory tree."""
    if isinstance(node, dict):
        if node.get("t") == "Image":
            location = node["c"][2][0]
            if urlparse(location).scheme and not Path(location).is_absolute():
                raise ValueError(f"Use a local image asset for reproducible exports: {location}")
            path = (source_dir / unquote(location)).resolve()
            if not path.is_file():
                raise ValueError(f"Image not found: {location}")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
            # Stable safe basename: TeX paths need not escape the source filename.
            destination = output / "assets" / (digest + path.suffix.lower())
            destination.parent.mkdir(exist_ok=True)
            if path != destination:
                shutil.copy2(path, destination)
            node["c"][2][0] = destination.relative_to(output).as_posix()
        for value in node.values():
            local_assets(value, source_dir, output)
    elif isinstance(node, list):
        for value in node:
            local_assets(value, source_dir, output)


def check_pdf_links(path: Path) -> list[str]:
    """Validate existing internal destinations; impose no citation-count minimum."""
    from pypdf import PdfReader
    reader = PdfReader(path)
    named = reader.named_destinations
    pages = {page.indirect_reference.idnum for page in reader.pages}
    findings = []
    for page_number, page in enumerate(reader.pages, 1):
        for reference in page.get("/Annots", []):
            annotation = reference.get_object()
            action = annotation.get("/A", {})
            destination = annotation.get("/Dest")
            if action.get("/S") == "/GoTo":
                destination = action.get("/D")
                if destination is None:
                    findings.append(f"PDF page {page_number}: GoTo has no destination")
            if destination is None:
                continue
            if isinstance(destination, str):
                if destination not in named:
                    findings.append(f"PDF page {page_number}: missing destination {destination}")
                elif reader.get_destination_page_number(named[destination]) is None:
                    findings.append(f"PDF page {page_number}: destination has no page {destination}")
            elif not destination or getattr(destination[0], "idnum", None) not in pages:
                findings.append(f"PDF page {page_number}: invalid internal page destination")
    return findings


def _table_style_index(xml: bytes, origin: str) -> dict:
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise ValueError(f"{origin} word/styles.xml is invalid: {exc}") from exc
    ids, names, all_ids = {}, {}, {}
    for style in root.findall(f"{{{W_NS}}}style"):
        identifier = style.get(f"{{{W_NS}}}styleId", "")
        kind = style.get(f"{{{W_NS}}}type", "")
        all_ids.setdefault(identifier, []).append(kind)
        if kind != "table":
            continue
        ids[identifier] = ids.get(identifier, 0) + 1
        name = style.find(f"{{{W_NS}}}name")
        if name is not None:
            names.setdefault(name.get(f"{{{W_NS}}}val", ""), []).append(identifier)
    return {"origin": origin, "ids": ids, "names": names, "all_ids": all_ids}


def _resolve_table_style(value: str, output: dict, reference: dict | None) -> str:
    indexes = [output] + ([reference] if reference is not None else [])
    # An actual table ID is authoritative; an unrelated display-name collision
    # must not change an already valid reference.
    for index in indexes:
        count = index["ids"].get(value, 0)
        if count:
            if count != 1:
                raise ValueError(f"Table style {value!r}: duplicate table styleId in {index['origin']}; give each table style a unique ID.")
            if output["ids"].get(value) != 1:
                raise ValueError(f"Table style {value!r} from reference DOCX is missing as a unique table style in output word/styles.xml; preserve that style in the reference/export.")
            return value
    candidates = set()
    for index in indexes:
        matches = index["names"].get(value, [])
        if len(matches) > 1:
            raise ValueError(f"Table style name {value!r} is ambiguous in {index['origin']} (table IDs: {', '.join(sorted(matches))}); use the intended table styleId in custom-style.")
        candidates.update(matches)
    if len(candidates) > 1:
        raise ValueError(f"Table style name {value!r} maps to conflicting reference/output table IDs: {', '.join(sorted(candidates))}; use the intended table styleId in custom-style.")
    if not candidates:
        raise ValueError(f"Table style {value!r} has no matching table style ID or display name in reference/output DOCX; set custom-style to an existing table style (paragraph/character styles do not apply).")
    identifier = candidates.pop()
    if not identifier or output["ids"].get(identifier) != 1:
        raise ValueError(f"Table style {value!r} resolves to {identifier!r}, which is missing or duplicated in output word/styles.xml; preserve a unique table style definition in the reference/export.")
    return identifier


def _table_style_edits(xml: bytes, output: dict, reference: dict | None) -> tuple[list, list]:
    """Locate only tblStyle/@val bytes; never serialize fields or namespaces."""
    parser = expat.ParserCreate(namespace_separator="}")
    parser.namespace_prefixes = True
    stack, edits, resolved = [], [], []
    table_path = [(W_NS, name) for name in ("tbl", "tblPr", "tblStyle")]

    def start(name, attributes):
        stack.append(tuple(name.split("}")[:2]))
        if stack[-3:] != table_path:
            return
        attribute = next((key for key in attributes if key.split("}")[:2] == [W_NS, "val"]), None)
        if attribute is None:
            raise ValueError("Word table tblStyle has no val; set custom-style to an existing table style ID or name.")
        value = attributes[attribute]
        identifier = _resolve_table_style(value, output, reference)
        resolved.append(identifier)
        if identifier == value:
            return
        # Expat supplies the original byte offset and namespace prefix. The
        # bounded lexical match preserves quote style and every unrelated byte.
        offset = parser.CurrentByteIndex
        tag = re.match(rb'''<(?:[^>"']|"[^"]*"|'[^']*')*>''', xml[offset:])
        prefix = attribute.split("}")[2:]
        qualified = ((prefix[0] + ":") if prefix else "") + "val"
        if tag:
            for match in re.finditer(rb'''([^\s=<>/'"]+)\s*=\s*(["'])(.*?)\2''', tag.group(), re.DOTALL):
                if match.group(1) == qualified.encode("utf-8"):
                    replacement = escape(identifier, {'"': '&quot;', "'": '&apos;'}).encode("utf-8")
                    edits.append((offset + match.start(3), offset + match.end(3), replacement))
                    return
        raise ValueError(f"Cannot locate UTF-8 tblStyle value {value!r}; re-export the DOCX with Pandoc before resolving table styles.")

    def reject_doctype(*_):
        raise ValueError("DOCX document.xml must not contain a DTD; re-export the document.")

    parser.StartElementHandler = start
    parser.EndElementHandler = lambda _: stack.pop()
    parser.StartDoctypeDeclHandler = reject_doctype
    try:
        parser.Parse(xml, True)
    except expat.ExpatError as exc:
        raise ValueError(f"Output word/document.xml is invalid: {exc}") from exc
    return edits, resolved


def _append_figure_table_style(xml: bytes) -> bytes:
    """Append Pandoc's absent layout-table style without serializing existing XML."""
    parser = expat.ParserCreate(namespace_separator="}")
    depth, root_start, root_end = 0, 0, 0

    def start(name, _attributes):
        nonlocal depth, root_start
        if depth == 0:
            if name != f"{W_NS}}}styles":
                raise ValueError("Output word/styles.xml has no Word styles root.")
            root_start = parser.CurrentByteIndex
        depth += 1

    def end(_name):
        nonlocal depth, root_end
        depth -= 1
        if depth == 0:
            root_end = parser.CurrentByteIndex

    def reject_doctype(*_):
        raise ValueError("DOCX styles.xml must not contain a DTD; re-export the document.")

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.StartDoctypeDeclHandler = reject_doctype
    try:
        parser.Parse(xml, True)
    except expat.ExpatError as exc:
        raise ValueError(f"Output word/styles.xml is invalid: {exc}") from exc
    # No basedOn, font, shading, or scientific table formatting. Explicit nil
    # borders prevent inherited borders on Pandoc's figure-layout container.
    style = (f'<w:style xmlns:w="{W_NS}" w:type="table" w:styleId="FigureTable">'
             '<w:name w:val="FigureTable"/><w:tblPr><w:tblBorders>'
             + ''.join(f'<w:{edge} w:val="nil"/>' for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
             + '</w:tblBorders></w:tblPr></w:style>').encode('utf-8')
    if xml[root_end:root_end + 2] == b'</':
        return xml[:root_end] + style + xml[root_end:]
    # A styles document may be empty and use a self-closing root.
    tag = re.match(rb'''<([^\s/>]+)(?:[^>"']|"[^"]*"|'[^']*')*>''', xml[root_start:])
    if tag and tag.group().endswith(b'/>'):
        end_tag = root_start + tag.end()
        return xml[:end_tag - 2] + b'>' + style + b'</' + tag.group(1) + b'>' + xml[end_tag:]
    raise ValueError("Cannot locate UTF-8 styles root for FigureTable; re-export the DOCX with Pandoc.")


def resolve_docx_table_styles(path: Path, reference_doc: Path | None = None) -> int:
    """Resolve names and supply only an absent, used Pandoc FigureTable style."""
    with zipfile.ZipFile(path) as document:
        entries = [(info, document.read(info)) for info in document.infolist()]
        comment = document.comment
    payload = {info.filename: data for info, data in entries}
    if len(payload) != len(entries):
        raise ValueError("Output DOCX contains duplicate ZIP members; re-export the document.")
    if "word/styles.xml" not in payload or "word/document.xml" not in payload:
        raise ValueError("Output DOCX needs word/styles.xml and word/document.xml to resolve table styles.")
    styles_xml = payload["word/styles.xml"]
    output = _table_style_index(styles_xml, "output DOCX")
    reference = None
    if reference_doc is not None:
        with zipfile.ZipFile(reference_doc) as document:
            if "word/styles.xml" not in document.namelist():
                raise ValueError("Reference DOCX has no word/styles.xml; supply a Word reference document with table styles.")
            reference = _table_style_index(document.read("word/styles.xml"), "reference DOCX")
    xml = payload["word/document.xml"]
    try:
        document_root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise ValueError(f"Output word/document.xml is invalid: {exc}") from exc
    used_figure_table = any(node.get(f"{{{W_NS}}}val") == "FigureTable" for node in
                           document_root.findall(f".//{{{W_NS}}}tbl/{{{W_NS}}}tblPr/{{{W_NS}}}tblStyle"))
    if used_figure_table:
        indexes = [output] + ([reference] if reference is not None else [])
        for index in indexes:
            kinds = index['all_ids'].get('FigureTable', [])
            if any(kind != 'table' for kind in kinds):
                raise ValueError(f"FigureTable styleId conflicts with a non-table style in {index['origin']}; use a unique table style ID, without duplicating the existing ID.")
        # Explicit IDs/names (including ambiguous names) remain owned by the
        # normal resolver. In particular, a lost reference style is not rebuilt.
        if not any('FigureTable' in index['all_ids'] or 'FigureTable' in index['names'] for index in indexes):
            styles_xml = _append_figure_table_style(styles_xml)
            output = _table_style_index(styles_xml, "output DOCX")
    added_style = styles_xml != payload["word/styles.xml"]
    edits, expected = _table_style_edits(xml, output, reference)
    if not edits and not added_style:
        return 0
    for start, end, replacement in reversed(edits):
        xml = xml[:start] + replacement + xml[end:]
    pending, actual = _table_style_edits(xml, output, reference)
    if pending or actual != expected:
        raise RuntimeError("DOCX table style resolution did not read back consistently; output was not changed.")
    updates = {"word/document.xml": xml, "word/styles.xml": styles_xml}
    fd, temporary_name = tempfile.mkstemp(prefix=".table-styles-", suffix=".docx", dir=path.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, "w") as document:
            document.comment = comment
            for info, data in entries:
                document.writestr(info, updates.get(info.filename, data))
        with zipfile.ZipFile(temporary) as document:
            if document.namelist() != list(payload) or document.comment != comment:
                raise RuntimeError("DOCX ZIP members changed during table style resolution; output was not changed.")
            for info, data in entries:
                expected_bytes = updates.get(info.filename, data)
                if document.read(info.filename) != expected_bytes:
                    raise RuntimeError(f"DOCX member {info.filename} failed byte readback; output was not changed.")
            saved_styles = _table_style_index(document.read("word/styles.xml"), "saved output DOCX")
            pending, actual = _table_style_edits(document.read("word/document.xml"), saved_styles, reference)
            if pending or actual != expected:
                raise RuntimeError("Saved DOCX table style references failed readback; output was not changed.")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return len(edits) + int(added_style)


def _docx_writer_ast(ast: dict) -> dict:
    """Keep consumed citeproc inputs out of Word's custom document properties.

    These are Pandoc build keys, regardless of Windows/POSIX/UNC path syntax
    or metadata value type. Preserve all scientific/publication metadata and
    the original semantic result for other writers and author layout filters.
    """
    return {**ast, "meta": {key: value for key, value in ast.get("meta", {}).items()
                           if key not in ("bibliography", "csl")}}


def bibliography_reader_input(pandoc: str, source: Path, output: Path) -> tuple[Path, list[dict]]:
    """Preserve BibLaTeX article IDs and initials through one CSL JSON input."""
    if source.suffix.lower() != ".bib":
        return source, []
    items = json.loads(run([pandoc, str(source), "--from", "biblatex", "--to", "csljson"], source.parent))
    text = source.read_text(encoding="utf-8-sig")
    starts = list(re.finditer(r"(?m)^\s*@\w+\s*\{\s*([^,\s]+)\s*,", text))
    eids = {}
    for index, match in enumerate(starts):
        entry = text[match.end():starts[index + 1].start() if index + 1 < len(starts) else len(text)]
        eid = re.search(r'(?mi)^\s*eid\s*=\s*(?:\{([^{}]*)\}|"([^"\n]*)"|(\d+))\s*,?\s*$', entry)
        if eid:
            eids[match.group(1)] = next(value for value in eid.groups() if value is not None).strip()
        elif re.search(r"(?mi)^\s*eid\s*=", entry):
            raise ValueError(f"Unsupported eid expression for {match.group(1)}; preserve the article identifier in a supported bibliography field before export.")
    changes = []
    for item in items:
        if item.get("id") in eids and not item.get("page"):
            item["page"] = eids[item["id"]]
            changes.append({"id": item["id"], "field": "page", "source_field": "eid", "value": item["page"]})
        # Citeproc initializes ASCII hyphenated given names correctly, but
        # U+2010/U+2011 names otherwise lose the following initial. Work on
        # parsed given names only; family/compound/literal names stay intact.
        for names in item.values():
            if isinstance(names, list):
                for name in names:
                    if isinstance(name, dict) and isinstance(name.get("given"), str):
                        before = name["given"]
                        name["given"] = before.replace("\u2010", "-").replace("\u2011", "-")
                        if name["given"] != before:
                            changes.append({"id": item["id"], "field": "given", "before": before, "after": name["given"], "family": name.get("family")})
    if not changes:
        return source, []
    path = output / (source.stem + ".citeproc.json")
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return path, changes


def _keep_docx_table_headers(xml: bytes) -> bytes:
    """Link leading header rows to the first data row without serializing XML.

    Word applies paragraph keepNext across table rows. Apply it to each header
    cell paragraph, but never to a data row: long tables must still paginate.
    Explicit local keepNext (including false) remains authoritative.
    """
    parser = expat.ParserCreate(namespace_separator="}")
    nodes, stack = [], []
    opening_tag = re.compile(rb'''<(?:[^>"']|"[^"]*"|'[^']*')*>''')

    def start(name, attrs):
        offset = parser.CurrentByteIndex
        opening_end = opening_tag.match(xml, offset).end()
        node = {"name": name, "attrs": attrs, "start": offset,
                "opening_end": opening_end, "children": []}
        if stack:
            stack[-1]["children"].append(node)
        nodes.append(node)
        stack.append(node)

    def end(name):
        stack.pop()

    parser.StartElementHandler, parser.EndElementHandler = start, end
    parser.Parse(xml, True)
    word = W_NS + "}"

    def child(node, name):
        return next((item for item in node["children"] if item["name"] == word + name), None)

    edits = []

    def keep_next(paragraph):
        properties = child(paragraph, "pPr")
        if properties is not None and child(properties, "keepNext") is not None:
            return
        opening = xml[paragraph["start"]:paragraph["opening_end"]]
        prefix = re.match(rb"<([^\s:>]+):", opening).group(1)
        rule = b"<" + prefix + b":keepNext/>"
        if properties is None:
            properties_xml = b"<" + prefix + b":pPr>" + rule + b"</" + prefix + b":pPr>"
            if opening.endswith(b"/>"):
                edits.append((paragraph["start"], paragraph["opening_end"],
                              opening[:-2] + b">" + properties_xml + b"</" + prefix + b":p>"))
            else:
                offset = paragraph["opening_end"]
                edits.append((offset, offset, properties_xml))
        else:
            opening = xml[properties["start"]:properties["opening_end"]]
            if opening.endswith(b"/>"):
                edits.append((properties["start"], properties["opening_end"],
                              opening[:-2] + b">" + rule + b"</" + prefix + b":pPr>"))
            else:
                style = child(properties, "pStyle")
                offset = style["opening_end"] if style is not None else properties["opening_end"]
                # pStyle is an empty property in valid WordprocessingML.
                if style is not None and not xml[style["start"]:offset].endswith(b"/>"):
                    offset = xml.index(b">", xml.index(b"</", offset)) + 1
                edits.append((offset, offset, rule))

    def header_paragraphs(node):
        for item in node["children"]:
            if item["name"] == word + "p":
                keep_next(item)
            elif item["name"] != word + "tbl":
                header_paragraphs(item)

    for parent in nodes:
        for index, table in enumerate(parent["children"]):
            if table["name"] != word + "tbl":
                continue
            rows = [item for item in table["children"] if item["name"] == word + "tr"]
            headers = []
            for row in rows:
                properties = child(row, "trPr")
                header = child(properties, "tblHeader") if properties is not None else None
                if header is None or header["attrs"].get(word + "val", "1").lower() in ("0", "false", "off"):
                    break
                headers.append(row)
            if not headers or len(headers) == len(rows):
                continue
            for header in headers:
                header_paragraphs(header)
            if index:
                caption = parent["children"][index - 1]
                properties = child(caption, "pPr") if caption["name"] == word + "p" else None
                style = child(properties, "pStyle") if properties is not None else None
                if style is not None and style["attrs"].get(word + "val", "").lower() in ("tablecaption", "caption"):
                    keep_next(caption)
    for begin, finish, replacement in sorted(edits, reverse=True):
        xml = xml[:begin] + replacement + xml[finish:]
    return xml


def keep_docx_table_rows(path: Path) -> int:
    """Keep rows intact and headers with first data; return added cantSplit count.

    Existing explicit rules win. Oversized rows still need actual Word review.
    """
    with zipfile.ZipFile(path) as document:
        entries = [(info, document.read(info)) for info in document.infolist()]
        comment = document.comment
    count = 0
    def row(match):
        nonlocal count
        data = match.group()
        if re.search(rb"<w:cantSplit\b", data):
            return data
        count += 1
        properties = re.search(rb"<w:trPr\b[^>]*>", data)
        if properties:
            tag = properties.group()
            replacement = tag[:-2] + b"><w:cantSplit/></w:trPr>" if tag.endswith(b"/>") else tag + b"<w:cantSplit/>"
            return data[:properties.start()] + replacement + data[properties.end():]
        return re.sub(rb"(<w:tr\b[^>]*>)", rb"\1<w:trPr><w:cantSplit/></w:trPr>", data, count=1)
    payload = next(data for info, data in entries if info.filename == "word/document.xml")
    updated = re.sub(rb"<w:tr\b[^>]*>.*?</w:tr>", row, payload, flags=re.DOTALL)
    updated = _keep_docx_table_headers(updated)
    if updated == payload:
        return 0
    ElementTree.fromstring(updated)
    fd, name = tempfile.mkstemp(prefix=".table-rows-", suffix=".docx", dir=path.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        with zipfile.ZipFile(temporary, "w") as document:
            document.comment = comment
            for info, data in entries:
                document.writestr(info, updated if info.filename == "word/document.xml" else data)
        with zipfile.ZipFile(temporary) as document:
            for info, data in entries:
                if document.read(info.filename) != (updated if info.filename == "word/document.xml" else data):
                    raise RuntimeError("Word row pagination failed byte readback; output was not changed.")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return count


def word_pdf_assets(ast: dict, output: Path, pdftocairo: str = "") -> list[dict]:
    """Render single-page figure PDFs in the Word-only AST; keep PDF assets intact."""
    records = []
    def visit(node, figure_id=""):
        if isinstance(node, dict):
            if node.get("t") == "Figure":
                figure_id = node["c"][0][0]
            if node.get("t") == "Image" and Path(node["c"][2][0]).suffix.lower() == ".pdf":
                source = (output / node["c"][2][0]).resolve()
                destination = source.with_suffix(".word.png")
                if pdftocairo:
                    rasterizer = Path(pdftocairo).resolve()
                    info = rasterizer.with_name("pdfinfo" + rasterizer.suffix)
                    if not rasterizer.is_file() or not info.is_file():
                        raise ValueError("--pdftocairo needs that executable and adjacent pdfinfo for single-page validation.")
                    pages = re.search(r"^Pages:\s+(\d+)", run([str(info), str(source)], output), re.MULTILINE)
                    if pages is None or int(pages.group(1)) != 1:
                        raise ValueError(f"Word figure PDF needs an explicit single-page selection: {source}")
                    # Some Windows Poppler builds cannot create Unicode output
                    # filenames; the export assets already have ASCII hash names.
                    run([str(rasterizer), "-png", "-singlefile", "-r", "300", source.name, destination.with_suffix("").name], source.parent)
                    renderer = str(rasterizer)
                else:
                    try:
                        import fitz
                    except ImportError as exc:
                        raise ValueError("Word PDF figures need PyMuPDF or --pdftocairo pointing to existing local Poppler tools; no Word file was exported.") from exc
                    with fitz.open(source) as document:
                        if len(document) != 1:
                            raise ValueError(f"Word figure PDF needs an explicit single-page selection: {source}")
                        document[0].get_pixmap(dpi=300, alpha=False).save(destination)
                    renderer = "PyMuPDF " + fitz.VersionBind
                node["c"][2][0] = destination.relative_to(output).as_posix()
                records.append({"figure_id": figure_id, "source": str(source),
                                "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                                "output": str(destination), "output_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                                "scope": "Word-only media; canonical PDF/semantic source preserved", "dpi": 300, "renderer": renderer})
            for value in node.values():
                visit(value, figure_id)
        elif isinstance(node, list):
            for value in node:
                visit(value, figure_id)
    visit(ast)
    return records


def check_template_body(pandoc: str, template: Path, ast: dict, cwd: Path) -> None:
    """Ask Pandoc whether this template consumes the manuscript body.

    Supports partials and conditionals without guessing template syntax. A
    publisher's standalone sample can otherwise compile while replacing the
    actual manuscript. This check does not certify the template's official origin.
    """
    marker = "PaperSpineBodyProbe" + os.urandom(16).hex()
    probe = {**ast, "blocks": [{"t": "Plain", "c": [{"t": "Str", "c": marker}]}]}
    rendered = run([pandoc, "-", "--from", "json", "--to", "latex", "--standalone",
                    "--template", str(template.resolve())],
                   cwd, input_text=json.dumps(probe, ensure_ascii=False))
    if marker not in rendered:
        raise ValueError(
            f"Template does not render the manuscript body: {template}. "
            "--template requires a Pandoc template that emits $body$ (directly or "
            "through a partial). An official LaTeX class/sample is not automatically "
            "a Pandoc template: use its native LaTeX build, or adapt its wrapper "
            "while preserving the venue class and layout. No replacement paper was exported."
        )


def format_input_details(args: argparse.Namespace, formats: set[str]) -> dict:
    """Report actual supplied layout inputs without certifying their provenance."""
    details = {}
    for option, applicable in (
        ("template", bool(formats & {"tex", "pdf"})),
        ("reference_doc", "docx" in formats),
        ("metadata_file", True),
        ("csl", True),
    ):
        path = getattr(args, option, None)
        details[option] = (
            {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
             "applied": applicable}
            if path is not None else {"path": None, "applied": False}
        )
    details["scope"] = "Actual export inputs; official origin and venue suitability require source review."
    return details


def pandoc_longtable_input(text: str) -> tuple[str, int]:
    """Keep one scientific header/body while dropping TeX page-repeat furniture."""
    changed = 0
    def normalize(match):
        nonlocal changed
        table = match.group(0)
        if r"\endfirsthead" not in table:
            return table
        # Longtable stores first head, repeat head, footer and last footer
        # before its body. Keep the first head and body, omitting only the
        # explicitly delimited pagination material from the reader input.
        first_head, _, tail = table.partition(r"\endfirsthead")
        _, boundary, tail = tail.partition(r"\endhead")
        if not boundary:
            raise ValueError("longtable has endfirsthead without endhead; retain native TeX and repair that table before import.")
        for boundary in (r"\endfoot", r"\endlastfoot"):
            if boundary in tail:
                footer, _, remaining = tail.partition(boundary)
                # Footers may contain units or statistical notes. Only known
                # rules and continuation furniture are safe to omit; refuse
                # unfamiliar content instead of silently deleting science.
                furniture = re.sub(r"(?m)(?<!\\)%[^\n]*", "", footer)
                furniture = re.sub(r"\\(?:toprule|midrule|bottomrule|hline)\b", "", furniture)
                furniture = re.sub(r"\\multicolumn\{\d+\}\{[clr]\}\{\s*(?:\\small\s*)?(?:\\itshape\s*)?Continued(?:\s+on\s+(?:the\s+)?next\s+page)?\s*\}", "", furniture, flags=re.IGNORECASE)
                furniture = re.sub(r"\\\\(?:\[[^\]]*\])?", "", furniture)
                if furniture.strip():
                    label = re.search(r"\\label\{([^}]+)\}", table)
                    where = label.group(1) if label else "unlabelled longtable"
                    raise ValueError(f"{where}: {boundary} contains non-pagination text; preserve its units/notes in a semantic caption or table note, or use the native TeX build. Reader input was not produced.")
                tail = remaining
        table = first_head + tail
        changed += 1
        return table
    # Pandoc's reader applies arraybackslash as an argument-taking macro in
    # this common column modifier and silently drops the first cell token.
    # Remove only this known layout directive in reader input, retaining p
    # column widths and every scientific cell; native TeX is untouched.
    text = re.sub(r">\{\s*\\raggedright\s*\\arraybackslash\s*\}", "", text)
    text = re.sub(r"\\begin\{longtable\}.*?\\end\{longtable\}", normalize, text, flags=re.DOTALL)
    return text, changed


def export(args: argparse.Namespace) -> dict:
    source = args.source.resolve()
    output = args.output_dir.resolve()
    lua = Path(__file__).with_name("manuscript_refs.lua")
    if not lua.is_file():
        raise ValueError(f"Missing installed runtime dependency: {lua.name}")
    for path in (source, args.bibliography, args.csl, args.reference_doc, args.metadata_file, args.template, *args.lua_filter):
        if path is not None and not path.is_file():
            raise ValueError(f"Input not found: {path}")
    output.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    ast_path = output / f"{stem}.semantic.json"
    bibliography, bibliography_changes = bibliography_reader_input(args.pandoc, args.bibliography.resolve(), output)
    common = ["--lua-filter", str(lua)]
    reader = getattr(args, "source_format", "markdown")
    reader_input, input_text, latex_import = str(source), None, None
    if reader == "latex" and getattr(args, "latexpand", ""):
        input_text = run([str(Path(args.latexpand).resolve()), "--fatal", "--keep-comments", source.name], source.parent)
        input_text, tables = pandoc_longtable_input(input_text)
        flattened = output / f"{stem}.pandoc-input.tex"
        flattened.write_text(input_text, encoding="utf-8")
        reader_input = "-"
        latex_import = {"source": str(source), "flattened_input": str(flattened), "longtables_normalized": tables,
                        "scope": "Literal includes flattened; repeated table headers and recognized pagination furniture omitted; known raggedright/arraybackslash column modifier removed for reader safety; scientific footer text rejected; canonical source unchanged."}
    command = [args.pandoc, reader_input, "--from", reader, "--to", "json", *common,
               "--citeproc", "--bibliography", str(bibliography),
               "--csl", str(args.csl.resolve()), "--metadata", "link-citations=true"]
    if args.metadata_file:
        command.extend(["--metadata-file", str(args.metadata_file.resolve())])
    # All literal includes are already flattened. Isolate that reader from
    # local publisher .sty macro implementations (the native build retains
    # them); scientific macros in the flattened source remain available.
    reader_directory = output if input_text is not None else source.parent
    ast = json.loads(run(command, reader_directory, input_text=input_text))
    formats = set(args.formats)
    if args.template is not None and formats & {"tex", "pdf"}:
        check_template_body(args.pandoc, args.template, ast, source.parent)
    local_assets(ast, source.parent, output)
    ast_path.write_text(json.dumps(ast, ensure_ascii=False), encoding="utf-8")
    paths = {"semantic": str(ast_path),
             "format_inputs": format_input_details(args, formats),
             "render_diagnostics": {"status": "not_run", "reason": "pdf_not_requested", "findings": []}}
    if latex_import is not None:
        paths["latex_import"] = latex_import
    if bibliography_changes:
        paths["bibliography_reader_input"] = {"source": str(args.bibliography.resolve()), "reader_input": str(bibliography), "changes": bibliography_changes,
                                               "scope": "Reader-only article identifier/parsed given-name compatibility; original bibliography preserved."}
    layout = [item for path in args.lua_filter for item in ("--lua-filter", str(path.resolve()))]
    if "docx" in formats:
        docx = output / f"{stem}.docx"
        command = [args.pandoc, "-", "--from", "json", "--to", "docx", "--standalone", *common, *layout, "-o", str(docx)]
        if args.reference_doc:
            command.extend(["--reference-doc", str(args.reference_doc.resolve())])
        word_ast = json.loads(json.dumps(_docx_writer_ast(ast)))
        paths["word_media_conversions"] = word_pdf_assets(word_ast, output, getattr(args, "pdftocairo", ""))
        run(command, output, input_text=json.dumps(word_ast, ensure_ascii=False))
        resolve_docx_table_styles(docx, args.reference_doc)
        if getattr(args, "keep_table_rows", False):
            paths["word_rows_kept_intact"] = keep_docx_table_rows(docx)
        with zipfile.ZipFile(docx) as document:
            document_xml = document.read("word/document.xml")
            findings = internal_reference_findings(document_xml)
            repeated_markers = duplicate_figure_reference_findings(document_xml)
            placements, warnings = inspect_word_figure_geometry(
                document_xml,
                document.read("word/_rels/document.xml.rels") if "word/_rels/document.xml.rels" in document.namelist() else None,
                {name: document.read(name) for name in document.namelist() if name.startswith("word/media/")},
            )
        # A repeated printed prefix needs a producing-source repair, but must
        # not discard the useful conversion or prevent the other formats.
        # Broken destinations retain the existing structural failure behavior.
        structural = [item for item in findings if item not in repeated_markers]
        if structural:
            raise RuntimeError("\n".join(structural))
        paths["docx"] = str(docx)
        paths["word_diagnostics"] = {
            "status": "review_required" if findings or placements or warnings else "no_structural_findings",
            "reference_findings": findings, "figure_placements": placements,
            "figure_warnings": warnings,
            "figure_label_legibility": "unknown" if placements or warnings else "not_assessed",
            "scope": "Structural and placement diagnostics; final-size visual review and scientific review remain separate.",
        }
    if formats & {"tex", "pdf"}:
        tex = output / f"{stem}.tex"
        command = [args.pandoc, str(ast_path), "--from", "json", "--to", "latex", "--standalone", *common, *layout, "-o", str(tex)]
        if args.template:
            command.extend(["--template", str(args.template.resolve())])
        run(command, output)
        tex_text = tex.read_text(encoding="utf-8")
        findings = check_internal_destinations(tex_text) + check_labels_and_refs(tex_text)
        if findings:
            raise RuntimeError("\n".join(item.message for item in findings))
        paths["tex"] = str(tex)
        if "pdf" in formats:
            for _ in range(2):
                run([args.pdf_engine, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", tex.name], output)
            log_path = tex.with_suffix(".log")
            log = log_path.read_text(encoding="utf-8", errors="replace")
            paths["render_diagnostics"] = tex_render_diagnostics(log, log_path)
            if "There were undefined references" in log:
                raise RuntimeError("PDF has undefined references after compilation; inspect the TeX log.")
            paths["pdf"] = str(tex.with_suffix(".pdf"))
            findings = check_pdf_links(tex.with_suffix(".pdf"))
            if findings:
                raise RuntimeError("\n".join(findings))
    # Inspect the actual current source and generated manuscript surfaces. This
    # report locates possible problems; findings must be reviewed in context
    # rather than automatically deleted. Conversion and surface checks have
    # separate results so a caller cannot mistake converted files for approval.
    surface_sources = [source] if reader != "json" else []
    surface = validate_surface(sources=[*surface_sources, *(Path(paths[key]) for key in ("tex", "docx", "pdf") if key in paths)])
    report = output / "publication_surface_check.md"
    if report.resolve() == source:
        report = output / f"{stem}.surface-report.md"
    report.write_text(surface_markdown(surface), encoding="utf-8")
    paths["publication_surface_check"] = str(report)
    paths["conversion_succeeded"] = True
    paths["publication_surface"] = {
        **surface.__dict__,
        "status": "extraction_incomplete" if surface.errors else "review_required" if surface.matches else "no_rule_matches",
    }
    return paths


def main(argv=None) -> int:
    # Direct Windows launches may inherit a legacy code page even though
    # Pandoc and the manuscript use Unicode. Diagnostics are part of the
    # public JSON interface and must not turn a useful export into an error.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--source-format", choices=("markdown", "latex", "json"), default="markdown",
                        help="Pandoc input reader; existing TeX is read from its own directory with the same bibliography.")
    parser.add_argument("--bibliography", type=Path, required=True)
    parser.add_argument("--csl", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reference-doc", type=Path)
    parser.add_argument("--metadata-file", type=Path)
    parser.add_argument("--template", type=Path,
                        help="Pandoc LaTeX template that renders the manuscript body; not a raw publisher sample/class.")
    parser.add_argument("--lua-filter", type=Path, action="append", default=[],
                        help="Optional author layout filter, applied after semantic references to each writer; repeatable.")
    parser.add_argument("--pdf-engine", default="xelatex", choices=("xelatex", "lualatex", "pdflatex"))
    parser.add_argument("--pandoc", default="pandoc")
    parser.add_argument("--pdftocairo", default="",
                        help="Existing local pdftocairo executable (with adjacent pdfinfo) for Word-only PDF figure rendering; otherwise uses PyMuPDF.")
    parser.add_argument("--latexpand", default="",
                        help="Existing latexpand executable for TeX includes, including data rows inside tables; preserves the canonical TeX tree.")
    parser.add_argument("--keep-table-rows", action="store_true",
                        help="Keep Word rows intact and leading headers with the first data row, preserving explicit rules; inspect tall rows in the actual Word render.")
    parser.add_argument("--formats", nargs="+", choices=("docx", "tex", "pdf"), default=["docx", "tex", "pdf"])
    args = parser.parse_args(argv)
    try:
        result = export(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        status = result["publication_surface"]["status"]
        if status != "no_rule_matches":
            print(f"Conversion completed; publication surface {status}. Generated files are retained; "
                  f"inspect {result['publication_surface_check']} and repair/retry the same manuscript.", file=sys.stderr)
        rendering = result["render_diagnostics"]
        word_findings = result.get("word_diagnostics", {}).get("reference_findings", [])
        if word_findings:
            print("Conversion completed; Word reference text needs repair. Generated files are retained.", file=sys.stderr)
            for finding in word_findings:
                print(finding, file=sys.stderr)
        if rendering["status"] == "review_required":
            print("Conversion completed with missing glyphs; generated files are retained. "
                  "Repair font coverage or source notation and rerun the affected export.", file=sys.stderr)
            for finding in rendering["findings"]:
                print(f"{rendering['log_path']}:{finding['line']}: {finding['message']}", file=sys.stderr)
        return 3 if status == "extraction_incomplete" else 2 if (
            status == "review_required" or rendering["status"] == "review_required" or word_findings
        ) else 0
    except (ValueError, RuntimeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
