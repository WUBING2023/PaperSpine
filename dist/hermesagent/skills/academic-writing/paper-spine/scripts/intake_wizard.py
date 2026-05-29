#!/usr/bin/env python3
"""Create PaperSpine configuration from an interactive terminal wizard."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import textwrap
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path


WORKFLOWS = ("rewrite_existing", "build_from_materials")
SCENES = ("journal", "conference", "report_review", "competition")
TIERS = ("flash", "pro")
LANGUAGES = ("en", "zh")
UI_LANGUAGES = ("zh", "en")
WORD_OUTPUTS = ("none", "docx")
TRANSLATION_PACKAGES = ("none", "zh")
REFERENCE_MODES = ("local_first", "specified_paths", "web")
HUMANIZE_TIERS = ("none", "light", "medium", "heavy")
DETECTION_PLATFORMS = ("cnki", "weipu", "general")
GLOBAL_CONFIG_ENV = "PAPERSPINE_CONFIG_HOME"

CHOICE_FIELDS = {
    "workflow": WORKFLOWS,
    "scene": SCENES,
    "tier": TIERS,
    "output_language": LANGUAGES,
    "word_output": WORD_OUTPUTS,
    "translation_package": TRANSLATION_PACKAGES,
    "reference_mode": REFERENCE_MODES,
    "humanize_tier": HUMANIZE_TIERS,
    "detection_platform": DETECTION_PLATFORMS,
    "ui_language": UI_LANGUAGES,
}

FIELD_ORDER = (
    "workflow",
    "scene",
    "tier",
    "output_language",
    "word_output",
    "translation_package",
    "target_name",
    "draft_path",
    "materials_dir",
    "user_motivation",
    "official_urls",
    "reference_mode",
    "reference_paths",
    "citation_target_count",
    "special_requirements",
    "detection_platform",
    "humanize_tier",
    "ui_language",
)

CHOICE_HELP = {
    "workflow": {
        "rewrite_existing": ("改进已有初稿", "Improve an existing draft"),
        "build_from_materials": ("从素材文件夹从零构筑", "Build from a materials folder"),
    },
    "scene": {
        "journal": ("期刊论文", "Journal paper"),
        "conference": ("会议论文", "Conference paper"),
        "report_review": ("课程报告、技术报告或综述", "Report, technical report, or review"),
        "competition": ("竞赛论文或竞赛报告", "Competition paper or report"),
    },
    "tier": {
        "flash": ("轻量调研：3+3 篇样例加官方要求", "Light research: 3+3 examples plus official requirements"),
        "pro": ("深度调研：6+6 篇样例加官方要求", "Deep research: 6+6 examples plus official requirements"),
    },
    "output_language": {
        "en": ("英文最终稿", "English final output"),
        "zh": ("中文最终稿", "Chinese final output"),
    },
    "word_output": {
        "none": ("不额外生成 Word", "Do not generate Word"),
        "docx": ("生成并检查 Word 文件", "Generate and check DOCX"),
    },
    "translation_package": {
        "none": ("不翻译", "Do not translate"),
        "zh": ("生成完整中文翻译包", "Generate complete Chinese translation package"),
    },
    "reference_mode": {
        "local_first": ("默认先读取本地/当前工作文件夹，再补充网络来源", "Default: read local/current-folder references first, then supplement from web"),
        "specified_paths": ("只优先读取用户指定的本地参考文献路径", "Prefer user-specified local reference paths"),
        "web": ("主要从网络检索参考材料", "Mainly collect references from the web"),
    },
    "ui_language": {
        "zh": ("中文界面", "Chinese interface"),
        "en": ("English UI", "English interface"),
    },
    "humanize_tier": {
        "none": ("不降 AI 痕迹", "No humanization"),
        "light": ("轻度 — 替换连接词，微调句式", "Light — replace connectors, vary sentence length"),
        "medium": ("中度 — 句式打散 + 信息密度 + 第一人称", "Medium — break patterns + density + first-person"),
        "heavy": ("强度 — 结构不规整 + 术语变体（保持学术语气）", "Heavy — structural variation + term variants (academic tone)"),
    },
    "detection_platform": {
        "cnki": ("知网 AIGC 检测", "CNKI AIGC detection"),
        "weipu": ("维普 AIGC 检测", "Weipu AIGC detection"),
        "general": ("通用策略 — 跨平台兼容", "General — cross-platform compatible"),
    },
}

LABELS = {
    "zh": {
        "banner": "PaperSpine 配置向导",
        "welcome": "Welcome back!",
        "tagline": "动机驱动的论文/报告 Skill Suite",
        "flowline": "先学习目标场景，再确认动机，最后构筑可审计的 LaTeX 成果",
        "why_1": "我们做 PaperSpine，是为了让 AI 先学习，再写作。",
        "why_2": "不是把论文润色得更长，而是把动机、证据与结构连成一条清晰主线。",
        "why_3": "它面向论文、报告与竞赛写作：调研目标场景，学习优秀样例，再逐段生成。",
        "continue": "按任意键进入配置",
        "workflow": "工作流",
        "scene": "目标场景",
        "tier": "调研深度",
        "output_language": "最终输出语言",
        "word_output": "Word 版本",
        "translation_package": "生成英文产物后是否翻译",
        "ui_language": "界面语言",
        "humanize_tier": "降 AI 痕迹",
        "detection_platform": "目标检测平台",
        "target_name": "目标名称",
        "draft_path": "初稿路径",
        "materials_dir": "素材文件夹路径",
        "user_motivation": "初始动机假设",
        "official_urls": "官方链接",
        "reference_mode": "文献读取模式",
        "reference_paths": "本地参考文献路径",
        "citation_target_count": "最终引用目标数",
        "special_requirements": "特殊要求",
        "review": "检查配置",
        "confirm": "确认写入配置",
        "edit": "输入要修改的字段编号，或直接回车完成",
        "invalid": "输入无效，请重新选择。",
        "wrote": "已写入",
        "keyboard_help": "←/→ 切换选项；↑/↓ 切换字段；Enter 编辑/确认；S 保存；Q 退出",
        "keyboard_subtitle": "上下切换字段，左右切换选项，所有路径与清单字段可按 Enter 直接编辑。",
        "progress": "进度",
        "current_value": "当前值",
        "fields_header": "配置字段",
        "previous": "上一个",
        "next": "下一个",
        "current_marker": "当前",
        "choice_hint": "左右键切换候选项，当前项位于中间。",
        "text_field_hint": "该字段已尽量从当前文件夹自动读取；Enter 可手动覆盖。",
        "save_hint": "检查无误后按 S 或 Enter 保存配置。",
        "text_help": "输入新内容。列表字段可用分号分隔。直接回车保留当前值。",
        "last_field_hint": "←/→ 切换语言，按 Enter 保存并退出。",
        "save": "保存并退出",
        "quit": "退出但不保存",
        "auto": "自动读取",
        "enter_edit": "Enter 修改",
        "empty": "空",
    },
    "en": {
        "banner": "PaperSpine Configuration Wizard",
        "welcome": "Welcome back!",
        "tagline": "Motivation-driven paper/report skill suite",
        "flowline": "Learn the target scene, confirm motivation, then build auditable LaTeX",
        "why_1": "PaperSpine exists so AI learns before it writes.",
        "why_2": "It does not make papers longer; it connects motivation, evidence, and structure.",
        "why_3": "For papers, reports, and competitions: research the scene, learn strong examples, then draft unit by unit.",
        "continue": "Press any key to configure",
        "workflow": "Workflow",
        "scene": "Target scene",
        "tier": "Research tier",
        "output_language": "Final output language",
        "word_output": "Word output",
        "translation_package": "Translate after English output",
        "ui_language": "UI language",
        "humanize_tier": "AI humanization",
        "detection_platform": "Detection platform",
        "target_name": "Target name",
        "draft_path": "Draft path",
        "materials_dir": "Materials directory",
        "user_motivation": "Initial motivation hypothesis",
        "official_urls": "Official URLs",
        "reference_mode": "Reference reading mode",
        "reference_paths": "Local reference paths",
        "citation_target_count": "Target citation count",
        "special_requirements": "Special requirements",
        "review": "Review configuration",
        "confirm": "Write config",
        "edit": "Enter field number to edit, or press Enter to finish",
        "invalid": "Invalid input. Please choose again.",
        "wrote": "Wrote",
        "keyboard_help": "Left/Right: option; Up/Down: field; Enter: edit/confirm; S: save; Q: quit",
        "keyboard_subtitle": "Use Up/Down for fields, Left/Right for choices, and Enter to edit paths or lists.",
        "progress": "Progress",
        "current_value": "Current value",
        "fields_header": "Fields",
        "previous": "Previous",
        "next": "Next",
        "current_marker": "Current",
        "choice_hint": "Use Left/Right to cycle choices. The active value is centered.",
        "text_field_hint": "Auto-filled from the current folder when possible. Press Enter to override.",
        "save_hint": "Press S or Enter to save after review.",
        "text_help": "Enter a new value. Separate list fields with semicolons. Press Enter to keep current.",
        "last_field_hint": "Left/Right to switch language, Enter to save and exit.",
        "save": "Save and exit",
        "quit": "Exit without saving",
        "auto": "Auto-read",
        "enter_edit": "Enter to edit",
        "empty": "empty",
    },
}


@dataclass
class PaperSpineConfig:
    workflow: str
    scene: str
    tier: str
    output_language: str
    target_name: str
    materials_dir: str
    draft_path: str
    user_motivation: str
    official_urls: list[str]
    reference_mode: str
    reference_paths: list[str]
    citation_target_count: int
    special_requirements: list[str]
    word_output: str
    translation_package: str
    humanize_tier: str
    detection_platform: str
    ui_language: str


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
URL_RE = re.compile(r"https?://[^\s)>\]]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create PaperSpine config files.")
    parser.add_argument("--output-dir", default="paper_rewriting_output")
    parser.add_argument("--workflow", choices=WORKFLOWS)
    parser.add_argument("--scene", choices=SCENES)
    parser.add_argument("--tier", choices=TIERS)
    parser.add_argument("--output-language", choices=LANGUAGES)
    parser.add_argument("--ui-language", choices=UI_LANGUAGES)
    parser.add_argument("--word-output", choices=WORD_OUTPUTS, default="none")
    parser.add_argument("--translation-package", choices=TRANSLATION_PACKAGES, default="none")
    parser.add_argument("--target-name", default="")
    parser.add_argument("--materials-dir", default="")
    parser.add_argument("--draft-path", default="")
    parser.add_argument("--user-motivation", default="")
    parser.add_argument("--official-url", action="append", default=[])
    parser.add_argument("--reference-mode", choices=REFERENCE_MODES, default="local_first")
    parser.add_argument("--reference-path", action="append", default=[])
    parser.add_argument("--citation-target-count", type=int, default=20)
    parser.add_argument("--special-requirement", action="append", default=[])
    parser.add_argument("--humanize-tier", choices=HUMANIZE_TIERS, default="none")
    parser.add_argument("--detection-platform", choices=DETECTION_PLATFORMS, default="general")
    parser.add_argument("--setup-global", action="store_true", help="Choose and save global PaperSpine UI preferences.")
    parser.add_argument("--no-interactive", action="store_true")
    parser.add_argument("--keyboard-ui", action="store_true", help="Use arrow-key terminal UI when a real Windows terminal is available.")
    parser.add_argument("--classic-input", action="store_true", help="Force numbered prompt input.")
    parser.add_argument("--preview-keyboard-frame", action="store_true", help="Print a static keyboard UI frame for tests/previews and exit.")
    parser.add_argument("--preview-width", type=int, default=118)
    return parser.parse_args()


def global_config_path() -> Path:
    base = os.environ.get(GLOBAL_CONFIG_ENV)
    if base:
        return Path(base) / "config.json"
    return Path.home() / ".paperspine" / "config.json"


def load_global_config() -> dict[str, str]:
    path = global_config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_global_config(data: dict[str, str]) -> None:
    path = global_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tr(ui_language: str, key: str) -> str:
    return LABELS.get(ui_language, LABELS["zh"]).get(key, key)


def configure_windows_console() -> None:
    if os.name != "nt" or not sys.stdout.isatty():
        return
    try:
        os.system("chcp 65001 > nul")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def help_text(key: str, value: str, ui_language: str) -> str:
    zh_help, en_help = CHOICE_HELP.get(key, {}).get(value, ("", ""))
    return zh_help if ui_language == "zh" else en_help


def ansi(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def char_width(char: str) -> int:
    if unicodedata.combining(char):
        return 0
    return 2 if unicodedata.east_asian_width(char) in {"F", "W"} else 1


def display_width(text: str) -> int:
    return sum(char_width(char) for char in strip_ansi(text))


def visible_len(text: str) -> int:
    return display_width(text)


def crop_plain(text: str, width: int) -> str:
    if width <= 1:
        return ""
    if display_width(text) <= width:
        return text
    current = 0
    chars: list[str] = []
    for char in text:
        next_width = current + char_width(char)
        if next_width > max(0, width - 1):
            break
        chars.append(char)
        current = next_width
    return "".join(chars) + "…"


def pad_ansi(text: str, width: int, align: str = "center") -> str:
    length = visible_len(text)
    if length > width:
        plain = ANSI_RE.sub("", text)
        text = crop_plain(plain, width)
        length = visible_len(text)
    gap = max(0, width - length)
    if align == "left":
        return text + " " * gap
    if align == "right":
        return " " * gap + text
    left = gap // 2
    return " " * left + text + " " * (gap - left)


def term_width(default: int = 118) -> int:
    return max(96, shutil.get_terminal_size((default, 36)).columns)


def term_height(default: int = 34) -> int:
    return max(24, shutil.get_terminal_size((118, default)).lines)


def wrap_plain(text: str, width: int, max_lines: int = 2) -> list[str]:
    text = " ".join(str(text).split()) or ""
    if not text:
        return [""]
    lines: list[str] = []
    current = ""
    current_width = 0
    for char in text:
        if char == "\n":
            lines.append(current)
            current = ""
            current_width = 0
            continue
        next_width = current_width + char_width(char)
        if next_width > width and current:
            lines.append(current.rstrip())
            current = char
            current_width = char_width(char)
            if len(lines) >= max_lines:
                break
        else:
            current += char
            current_width = next_width
    if current and len(lines) < max_lines:
        lines.append(current.rstrip())
    if len(lines) == max_lines and display_width(" ".join(lines)) < display_width(text):
        lines[-1] = crop_plain(lines[-1], max(1, width))
    return lines or [""]


def style(text: str, code: str, color: bool = True) -> str:
    return ansi(text, code) if color else text


def safe_input(prompt: str = "> ") -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def _read_key_windows() -> str:
    import msvcrt

    ch = msvcrt.getwch()
    if ch in ("\x00", "\xe0"):
        code = msvcrt.getwch()
        return {"H": "up", "P": "down", "K": "left", "M": "right"}.get(code, "")
    if ch in ("\r", "\n"):
        return "enter"
    if ch in ("s", "S"):
        return "save"
    if ch in ("q", "Q", "\x1b"):
        return "quit"
    return ch


def _read_key_unix() -> str:
    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            old_blocking = termios.tcgetattr(fd)
            try:
                attrs = termios.tcgetattr(fd)
                attrs[5][termios.VMIN] = 0
                attrs[5][termios.VTIME] = 1
                termios.tcsetattr(fd, termios.TCSANOW, attrs)
                nxt = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSANOW, old_blocking)
            if nxt == "[":
                code = sys.stdin.read(1)
                return {"A": "up", "B": "down", "C": "right", "D": "left"}.get(code, "")
            return "quit"
        if ch in ("\r", "\n"):
            return "enter"
        if ch in ("s", "S"):
            return "save"
        if ch in ("q", "Q"):
            return "quit"
        if ord(ch) == 3:
            raise KeyboardInterrupt()
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)


def read_key() -> str:
    if os.name == "nt":
        return _read_key_windows()
    return _read_key_unix()


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_banner(ui_language: str) -> None:
    title = tr(ui_language, "banner")
    line = "=" * max(48, len(title) + 8)
    print(f"\n{line}\n  {title}\n{line}")


def print_centered_box(lines: list[str], width: int, accent: str = "38;5;208") -> None:
    print(ansi("╭" + "─" * (width - 2) + "╮", accent))
    for line in lines:
        print(ansi("│", accent) + pad_ansi(line, width - 2) + ansi("│", accent))
    print(ansi("╰" + "─" * (width - 2) + "╯", accent))


def print_welcome_screen(ui_language: str, wait: bool = False) -> None:
    if not sys.stdout.isatty():
        print("PaperSpine v3")
        print(tr(ui_language, "welcome"))
        print(tr(ui_language, "flowline"))
        print(str(Path.cwd()))
        return
    if wait:
        clear_screen()
    width = min(term_width(), 126)
    accent = "38;5;250"
    white = "1;97"
    muted = "90"
    mountain = [
        "                    /\\                 /\\                         ",
        "          /\\       /  \\      /\\       /  \\        /\\              ",
        "   /\\    /  \\     /    \\    /  \\     /    \\      /  \\     /\\      ",
        "__/  \\__/    \\___/      \\__/    \\___/      \\____/    \\___/  \\__",
    ]
    title = [
        "██████╗  █████╗ ██████╗ ███████╗██████╗ ███████╗██████╗ ██╗███╗   ██╗███████╗",
        "██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██╔══██╗██║████╗  ██║██╔════╝",
        "██████╔╝███████║██████╔╝█████╗  ██████╔╝███████╗██████╔╝██║██╔██╗ ██║█████╗  ",
        "██╔═══╝ ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗╚════██║██╔═══╝ ██║██║╚██╗██║██╔══╝  ",
        "██║     ██║  ██║██║     ███████╗██║  ██║███████║██║     ██║██║ ╚████║███████╗",
    ]
    lines: list[str] = ["", ansi(tr(ui_language, "welcome"), muted), ""]
    lines.extend(ansi(line, white) for line in mountain)
    lines.append("")
    lines.extend(ansi(line, white) for line in title)
    lines.extend(
        [
            "",
            ansi(tr(ui_language, "tagline"), white),
            ansi(tr(ui_language, "flowline"), muted),
            "",
            tr(ui_language, "why_1"),
            tr(ui_language, "why_2"),
            tr(ui_language, "why_3"),
            "",
            ansi("X: Wbingo353332", muted),
            ansi("Douyin: 91362158854", muted),
            ansi("Xiaohongshu: 4770513150", muted),
            ansi("Bilibili: 彬_2023 (ID: 450856661)", muted),
            "",
            ansi(str(Path.cwd()), muted),
            "",
        ]
    )
    print()
    print(pad_ansi(ansi("PaperSpine v3", accent), width))
    print()
    for line in lines:
        print(pad_ansi(line, width))
    if wait:
        print()
        print(pad_ansi(ansi(tr(ui_language, "continue"), muted), width))
        read_key()


def choose(key: str, values: tuple[str, ...], ui_language: str, default: str | None = None) -> str:
    default = default or values[0]
    print(f"\n{tr(ui_language, key)}")
    for index, value in enumerate(values, start=1):
        suffix = " [default]" if value == default else ""
        description = help_text(key, value, ui_language)
        description = f" - {description}" if description else ""
        print(f"  {index}. {value}{suffix}{description}")
    while True:
        answer = safe_input("> ")
        if not answer:
            return default
        if answer.isdigit():
            idx = int(answer)
            if 1 <= idx <= len(values):
                return values[idx - 1]
        if answer in values:
            return answer
        print(tr(ui_language, "invalid"))


def ask_text(key: str, ui_language: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = safe_input(f"{tr(ui_language, key)}{suffix}: ")
    return answer or default


def split_items(value: str) -> list[str]:
    if not value:
        return []
    raw = value.replace("\n", ";").replace(",", ";").split(";")
    return [item.strip() for item in raw if item.strip()]


def default_language(scene: str) -> str:
    if scene in {"journal", "conference"}:
        return "en"
    return "zh"


def display_config(config: PaperSpineConfig) -> list[str]:
    data = asdict(config)
    keys = list(data)
    print("\n" + "-" * 72)
    for index, key in enumerate(keys, start=1):
        value = data[key]
        rendered = ", ".join(value) if isinstance(value, list) else value
        print(f"{index:>2}. {key}: {rendered}")
    print("-" * 72)
    return keys


def edit_config(config: PaperSpineConfig) -> PaperSpineConfig:
    while True:
        print(f"\n{tr(config.ui_language, 'review')}")
        keys = display_config(config)
        answer = safe_input(f"{tr(config.ui_language, 'confirm')} [Y/n]: ").lower()
        if answer in {"", "y", "yes"}:
            return config
        field = safe_input(f"{tr(config.ui_language, 'edit')}: ")
        if not field:
            return config
        if not field.isdigit() or not 1 <= int(field) <= len(keys):
            print(tr(config.ui_language, "invalid"))
            continue
        edit_field(config, keys[int(field) - 1], classic=True)


def can_use_keyboard_ui(force: bool = False) -> bool:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return False
    if os.name == "nt":
        try:
            import msvcrt  # noqa: F401
        except ImportError:
            return False
        return True
    try:
        import termios  # noqa: F401
        import tty  # noqa: F401
    except ImportError:
        return False
    return True


def rendered_value(config: PaperSpineConfig, field: str) -> str:
    value = getattr(config, field)
    if isinstance(value, list):
        return "; ".join(value)
    return str(value)


def option_triplet(config: PaperSpineConfig, field: str) -> tuple[str, str, str] | None:
    if field not in CHOICE_FIELDS:
        return None
    options = CHOICE_FIELDS[field]
    current = getattr(config, field)
    index = options.index(current) if current in options else 0
    return options[(index - 1) % len(options)], options[index], options[(index + 1) % len(options)]


def set_choice_value(config: PaperSpineConfig, field: str, direction: int) -> None:
    options = CHOICE_FIELDS[field]
    current = getattr(config, field)
    index = options.index(current) if current in options else 0
    setattr(config, field, options[(index + direction) % len(options)])
    normalize_config(config)


def edit_field(config: PaperSpineConfig, field: str, classic: bool = False) -> None:
    if field in CHOICE_FIELDS:
        if classic:
            setattr(config, field, choose(field, CHOICE_FIELDS[field], config.ui_language, getattr(config, field)))
            normalize_config(config)
        return
    clear_screen()
    print_banner(config.ui_language)
    print(f"{tr(config.ui_language, field)}")
    print(tr(config.ui_language, "text_help"))
    current = rendered_value(config, field)
    if current:
        print(f"\nCurrent: {current}")
    answer = safe_input("> ")
    if not answer:
        return
    if field in {"official_urls", "special_requirements", "reference_paths"}:
        setattr(config, field, split_items(answer))
    elif field == "citation_target_count":
        try:
            config.citation_target_count = int(answer)
        except ValueError:
            return
    else:
        setattr(config, field, answer)
    normalize_config(config)


def normalize_config(config: PaperSpineConfig) -> None:
    if config.output_language != "en":
        config.translation_package = "none"
    if config.workflow == "rewrite_existing":
        config.materials_dir = config.materials_dir or ""
    else:
        config.draft_path = config.draft_path or ""
    if config.reference_mode not in REFERENCE_MODES:
        config.reference_mode = "local_first"
    if not config.reference_paths:
        config.reference_paths = ["."]
    config.citation_target_count = max(1, int(config.citation_target_count or 20))


def find_first_existing_dir(names: tuple[str, ...]) -> str:
    cwd = Path.cwd()
    for name in names:
        if (cwd / name).is_dir():
            return name
    for path in cwd.iterdir():
        if path.is_dir() and path.name not in {"paper_rewriting_output", ".git", ".vscode"}:
            has_materials = any(path.glob(pattern) for pattern in ("*.md", "*.txt", "*.csv", "*.png", "*.jpg", "*.pdf", "*.docx"))
            if has_materials:
                return path.name
    return ""


def find_candidate_draft() -> str:
    cwd = Path.cwd()
    candidates: list[Path] = []
    for pattern in ("*.tex", "*.md", "*.docx", "*.pdf"):
        candidates.extend(path for path in cwd.glob(pattern) if path.is_file())
    candidates = [path for path in candidates if not path.name.lower().startswith("readme")]
    if not candidates:
        return ""
    preferred = ("draft", "manuscript", "paper", "main", "初稿", "论文")
    candidates.sort(key=lambda p: (0 if any(token in p.name.lower() for token in preferred) else 1, len(p.name)))
    return candidates[0].name


def read_small_text_files(root: Path, limit: int = 8) -> str:
    chunks: list[str] = []
    for path in root.rglob("*"):
        if len(chunks) >= limit:
            break
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        chunks.append(text[:2000])
    return "\n".join(chunks)


def infer_motivation(text: str, ui_language: str) -> str:
    markers = ("核心想法", "核心动机", "motivation", "Motivation", "主线", "创新点")
    for line in text.splitlines():
        clean = line.strip(" #：:*-")
        if any(marker in line for marker in markers) and 12 <= len(clean) <= 180:
            return clean
    if ui_language == "zh":
        return "请先调研目标场景和优秀样例，再生成候选动机并由用户确认。"
    return "Research the target scene and strong examples first, then propose motivation options for user confirmation."


def infer_urls(text: str) -> list[str]:
    seen: list[str] = []
    for match in URL_RE.findall(text):
        url = match.rstrip(".,;，。；")
        if url not in seen:
            seen.append(url)
    return seen[:6]


def auto_config_project(config: PaperSpineConfig, args: argparse.Namespace) -> None:
    cwd = Path.cwd()
    materials_dir = find_first_existing_dir(("materials", "素材", "source_materials", "data"))
    draft_path = find_candidate_draft()
    if not args.workflow:
        if materials_dir and not draft_path:
            config.workflow = "build_from_materials"
        elif draft_path:
            config.workflow = "rewrite_existing"
    if not args.materials_dir and materials_dir:
        config.materials_dir = materials_dir
    if not args.draft_path and draft_path:
        config.draft_path = draft_path
    if not args.target_name:
        config.target_name = cwd.name.replace("_", " ").replace("-", " ")
    material_root = cwd / config.materials_dir if config.materials_dir else cwd
    text = read_small_text_files(material_root if material_root.exists() else cwd)
    if not args.user_motivation:
        config.user_motivation = infer_motivation(text, config.ui_language)
    if not args.official_url:
        config.official_urls = infer_urls(text)
    if not args.reference_path:
        reference_dirs = [
            path.name
            for path in cwd.iterdir()
            if path.is_dir()
            and path.name.lower()
            in {"reference_materials", "references", "literature", "papers", "citations", "文献", "参考文献"}
        ]
        config.reference_paths = reference_dirs or ["."]
    if not args.special_requirement:
        requirements = [
            "必须输出 final_paper/main.tex；如果本机有 LaTeX 编译器则编译 paper.pdf。",
            "必须生成详细 writing_rationale_matrix.md，逐段解释写作逻辑。",
        ]
        figures_dir = material_root / "figures"
        if figures_dir.exists() and any(figures_dir.glob("*.*")):
            requirements.append("复制并引用素材图片到最终 LaTeX 项目的 figures/。")
        if config.workflow == "build_from_materials":
            requirements.append("从素材从零构筑，不把技术说明当成初稿润色。")
        config.special_requirements = requirements
    normalize_config(config)


def field_label(config: PaperSpineConfig, field: str, index: int, selected: bool, width: int) -> str:
    label = f"{index:02d}. {tr(config.ui_language, field)}"
    color = "1;97" if selected else "90"
    marker = ">" if selected else " "
    return pad_ansi(ansi(f"{marker} {label}", color), width, align="left")


def choice_columns(config: PaperSpineConfig, field: str, width: int, color: bool = True) -> list[str]:
    gray = "90"
    white = "1;97"
    triplet = option_triplet(config, field)
    if not triplet:
        return []
    prev, current, nxt = triplet
    slot = max(16, (width - 8) // 3)
    items = [
        ("<- " + tr(config.ui_language, "previous"), prev, gray),
        (tr(config.ui_language, "current_marker"), current, white),
        (tr(config.ui_language, "next") + " ->", nxt, gray),
    ]
    rows: list[list[str]] = []
    for marker, value, item_color in items:
        desc = help_text(field, value, config.ui_language) or value
        lines = [
            style(marker, item_color, color),
            style(value, item_color, color),
        ]
        lines.extend(style(line, item_color, color) for line in wrap_plain(desc, slot, max_lines=2))
        rows.append([pad_ansi(line, slot) for line in lines[:4]])
    while any(len(row) < 4 for row in rows):
        for row in rows:
            if len(row) < 4:
                row.append(" " * slot)
    return [
        rows[0][line] + "  " + rows[1][line] + "  " + rows[2][line]
        for line in range(4)
    ]


def text_value_lines(config: PaperSpineConfig, field: str, width: int, color: bool = True) -> list[str]:
    current = rendered_value(config, field) or tr(config.ui_language, "empty")
    current_lines = wrap_plain(current, max(24, width - 8), max_lines=4)
    lines = [
        style(tr(config.ui_language, "current_value"), "90", color),
        *[style(line, "1;97", color) for line in current_lines],
        "",
        style(tr(config.ui_language, "text_field_hint"), "90", color),
    ]
    return lines


def right_panel_lines(config: PaperSpineConfig, field: str, width: int, index: int, total: int, color: bool = True) -> list[str]:
    if field == "save":
        title = tr(config.ui_language, "save")
        lines = [
            style(title, "1;97", color),
            "",
            style(tr(config.ui_language, "save_hint"), "90", color),
            "",
            style("S / Enter", "1;97", color),
        ]
        return [pad_ansi(line, width) for line in lines]

    title = tr(config.ui_language, field)
    value = rendered_value(config, field) or tr(config.ui_language, "empty")
    header = f"{tr(config.ui_language, 'progress')} {index + 1}/{total - 1} · {title}"
    lines = [
        style(header, "1;97", color),
        style(f"{tr(config.ui_language, 'current_value')}: {crop_plain(value, max(12, width - 18))}", "90", color),
        "",
    ]
    if field in CHOICE_FIELDS:
        if index == total - 2:
            lines.append(style(tr(config.ui_language, "last_field_hint"), "1;97", color))
        else:
            lines.append(style(tr(config.ui_language, "choice_hint"), "90", color))
        lines.append("")
        lines.extend(choice_columns(config, field, width, color=color))
    else:
        lines.extend(text_value_lines(config, field, width, color=color))
    return [pad_ansi(line, width, align="left") for line in lines]


def render_keyboard_frame(
    config: PaperSpineConfig,
    index: int = 0,
    width: int | None = None,
    height: int | None = None,
    color: bool = True,
) -> list[str]:
    fields = list(FIELD_ORDER) + ["save"]
    index = max(0, min(index, len(fields) - 1))
    field = fields[index]
    width = max(96, min(width or term_width(), 140))
    height = max(24, height or term_height())
    left_w = max(30, int((width - 3) * 0.30))
    right_w = width - left_w - 3
    body_h = min(max(len(fields) + 2, 18), max(18, height - 7))
    accent = "38;5;244"
    muted = "90"

    left_items = [
        field_label(config, item, row + 1, row == index, left_w - 2)
        if item != "save"
        else pad_ansi(style(f"S. {tr(config.ui_language, 'save')}", "1;97" if row == index else muted, color), left_w - 2, align="left")
        for row, item in enumerate(fields)
    ]
    if len(left_items) > body_h:
        half = body_h // 2
        start = min(max(0, index - half), len(left_items) - body_h)
        left_items = left_items[start : start + body_h]
    top_pad = max(0, (body_h - len(left_items)) // 2)
    left_lines = [" " * (left_w - 2)] * top_pad + left_items
    left_lines += [" " * (left_w - 2)] * (body_h - len(left_lines))

    right_content = right_panel_lines(config, field, right_w - 2, index, len(fields), color=color)
    right_top_pad = max(0, (body_h - len(right_content)) // 2)
    right_lines = [" " * (right_w - 2)] * right_top_pad + right_content
    right_lines += [" " * (right_w - 2)] * (body_h - len(right_lines))

    top = style("╭" + "─" * (width - 2) + "╮", accent, color)
    split_top = style("├" + "─" * left_w + "┬" + "─" * right_w + "┤", accent, color)
    split_mid = style("├" + "─" * left_w + "┼" + "─" * right_w + "┤", accent, color)
    bottom = style("╰" + "─" * left_w + "┴" + "─" * right_w + "╯", accent, color)
    title = style("PaperSpine", "1;97", color) + style("  " + tr(config.ui_language, "banner"), muted, color)
    subtitle = style(tr(config.ui_language, "keyboard_subtitle"), muted, color)
    help_line = style(tr(config.ui_language, "keyboard_help"), muted, color)
    cwd_line = style("  " + str(Path.cwd()), muted, color)

    frame = [
        top,
        style("│", accent, color) + pad_ansi(title, width - 2) + style("│", accent, color),
        style("│", accent, color) + pad_ansi(subtitle, width - 2) + style("│", accent, color),
        style("│", accent, color) + pad_ansi(cwd_line, width - 2) + style("│", accent, color),
        split_top,
        style("│", accent, color)
        + pad_ansi(style(tr(config.ui_language, "fields_header"), muted, color), left_w)
        + style("│", accent, color)
        + pad_ansi(help_line, right_w)
        + style("│", accent, color),
        split_mid,
    ]
    for left, right in zip(left_lines, right_lines):
        frame.append(
            style("│", accent, color)
            + pad_ansi(left, left_w)
            + style("│", accent, color)
            + pad_ansi(right, right_w, align="left")
            + style("│", accent, color)
        )
    frame.append(bottom)
    return frame


def keyboard_editor(config: PaperSpineConfig) -> PaperSpineConfig:
    fields = list(FIELD_ORDER) + ["save"]
    index = 0
    while True:
        normalize_config(config)
        field = fields[index]
        clear_screen()
        print("\n".join(render_keyboard_frame(config, index=index, color=True)))
        key = read_key()
        if key == "up":
            index = (index - 1) % len(fields)
        elif key == "down":
            index = (index + 1) % len(fields)
        elif key == "left" and field in CHOICE_FIELDS:
            set_choice_value(config, field, -1)
        elif key == "right" and field in CHOICE_FIELDS:
            set_choice_value(config, field, 1)
        elif key == "enter":
            if field == "save":
                return config
            if field in CHOICE_FIELDS:
                if index == len(fields) - 2:
                    return config
                index = (index + 1) % len(fields)
            else:
                edit_field(config, field)
        elif key == "save":
            return config
        elif key == "quit":
            raise KeyboardInterrupt(tr(config.ui_language, "quit"))


def base_config_from_args(args: argparse.Namespace, ui_language: str) -> PaperSpineConfig:
    workflow = args.workflow or "rewrite_existing"
    scene = args.scene or "journal"
    output_language = args.output_language or default_language(scene)
    translation_package = args.translation_package
    if output_language != "en":
        translation_package = "none"
    config = PaperSpineConfig(
        workflow=workflow,
        scene=scene,
        tier=args.tier or "flash",
        output_language=output_language,
        target_name=args.target_name,
        materials_dir=args.materials_dir,
        draft_path=args.draft_path,
        user_motivation=args.user_motivation,
        official_urls=list(args.official_url),
        reference_mode=args.reference_mode,
        reference_paths=list(args.reference_path) or ["."],
        citation_target_count=max(1, args.citation_target_count),
        special_requirements=list(args.special_requirement),
        word_output=args.word_output,
        translation_package=translation_package,
        humanize_tier=args.humanize_tier,
        detection_platform=args.detection_platform,
        ui_language=ui_language,
    )
    if not args.no_interactive:
        auto_config_project(config, args)
    return config


def build_config(args: argparse.Namespace) -> PaperSpineConfig:
    global_config = load_global_config()
    ui_language = args.ui_language or global_config.get("ui_language", "zh")
    use_keyboard = (
        not args.classic_input
        and not args.no_interactive
        and (args.keyboard_ui or sys.stdin.isatty())
        and can_use_keyboard_ui(force=args.keyboard_ui)
    )

    if args.setup_global and not args.no_interactive:
        if use_keyboard:
            config = base_config_from_args(args, ui_language)
            print_welcome_screen(config.ui_language, wait=True)
            fields = ("ui_language", "save")
            index = 0
            while True:
                clear_screen()
                print_banner(config.ui_language)
                print(tr(config.ui_language, "keyboard_help"))
                for idx, field in enumerate(fields):
                    marker = ">" if idx == index else " "
                    label = tr(config.ui_language, field) if field != "save" else tr(config.ui_language, "save")
                    value = config.ui_language if field == "ui_language" else ""
                    print(f"{marker} {label:<18} {value}")
                key = read_key()
                if key in {"up", "down"}:
                    index = (index + 1) % len(fields)
                elif key in {"left", "right"} and fields[index] == "ui_language":
                    set_choice_value(config, "ui_language", 1 if key == "right" else -1)
                elif key in {"enter", "save"}:
                    break
                elif key == "quit":
                    raise KeyboardInterrupt(tr(config.ui_language, "quit"))
            ui_language = config.ui_language
        else:
            print_banner(ui_language)
            ui_language = choose("ui_language", UI_LANGUAGES, ui_language, default=ui_language)
        save_global_config({"ui_language": ui_language})
    elif args.setup_global:
        save_global_config({"ui_language": ui_language})

    config = base_config_from_args(args, ui_language)
    if args.no_interactive:
        return config

    if use_keyboard:
        print_welcome_screen(config.ui_language, wait=True)
        return keyboard_editor(config)

    print_welcome_screen(ui_language, wait=False)
    print_banner(ui_language)
    config.workflow = args.workflow or choose("workflow", WORKFLOWS, ui_language)
    config.scene = args.scene or choose("scene", SCENES, ui_language)
    config.tier = args.tier or choose("tier", TIERS, ui_language, default=config.tier)
    config.output_language = args.output_language or choose(
        "output_language", LANGUAGES, ui_language, default=config.output_language
    )
    config.word_output = choose("word_output", WORD_OUTPUTS, ui_language, default=config.word_output)
    if config.output_language == "en":
        config.translation_package = choose(
            "translation_package", TRANSLATION_PACKAGES, ui_language, default=config.translation_package
        )
    config.target_name = ask_text("target_name", ui_language, config.target_name)
    if config.workflow == "rewrite_existing":
        config.draft_path = ask_text("draft_path", ui_language, config.draft_path)
    else:
        config.materials_dir = ask_text("materials_dir", ui_language, config.materials_dir)
    config.user_motivation = ask_text("user_motivation", ui_language, config.user_motivation)
    config.official_urls.extend(split_items(ask_text("official_urls", ui_language)))
    config.reference_mode = choose("reference_mode", REFERENCE_MODES, ui_language, default=config.reference_mode)
    config.reference_paths = split_items(ask_text("reference_paths", ui_language, "; ".join(config.reference_paths)))
    raw_count = ask_text("citation_target_count", ui_language, str(config.citation_target_count))
    try:
        config.citation_target_count = int(raw_count)
    except ValueError:
        config.citation_target_count = 20
    config.special_requirements.extend(split_items(ask_text("special_requirements", ui_language)))
    normalize_config(config)
    return edit_config(config)


def markdown_config(config: PaperSpineConfig) -> str:
    data = asdict(config)
    lines = ["# PaperSpine Config", ""]
    for key, value in data.items():
        rendered = ", ".join(value) if isinstance(value, list) else value
        lines.append(f"- **{key}**: {rendered}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    configure_windows_console()
    args = parse_args()
    if args.preview_keyboard_frame:
        ui_language = args.ui_language or load_global_config().get("ui_language", "zh")
        config = base_config_from_args(args, ui_language)
        auto_config_project(config, args)
        print("\n".join(render_keyboard_frame(config, index=0, width=args.preview_width, color=False)))
        return 0
    config = build_config(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "paper_spine_config.json"
    md_path = output_dir / "paper_spine_config.md"
    json_path.write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown_config(config), encoding="utf-8")
    print(f"{tr(config.ui_language, 'wrote')} {json_path}")
    print(f"{tr(config.ui_language, 'wrote')} {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
