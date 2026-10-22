import ast
import subprocess
import sys
from pathlib import Path

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文本文件内容，用于代码审查",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出目录下的文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "目录路径"}
                },
                "required": ["directory"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_syntax_check",
            "description": "检查 Python 文件语法是否正确",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Python 文件路径"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_ruff",
            "description": "对 Python 文件运行 Ruff 静态检查",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Python 文件路径"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_lines",
            "description": "统计文件行数、空行、注释行",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"}
                },
                "required": ["path"],
            },
        },
    },
]


def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return f"错误：文件不存在 {path}"
    if not p.is_file():
        return f"错误：不是文件 {path}"

    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = p.read_text(encoding="gbk", errors="ignore")

    if len(text) > 20000:
        return text[:20000] + "\n\n...[内容过长，已截断]"
    return text


def list_files(directory: str) -> str:
    p = Path(directory)
    if not p.exists():
        return f"错误：目录不存在 {directory}"
    if not p.is_dir():
        return f"错误：不是目录 {directory}"

    files = []
    for item in sorted(p.rglob("*")):
        if item.is_file():
            rel = item.relative_to(p)
            files.append(str(rel))
        if len(files) >= 200:
            files.append("...[文件过多，已截断]")
            break

    return "\n".join(files) if files else "目录为空"


def run_syntax_check(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return f"错误：文件不存在 {path}"

    try:
        source = p.read_text(encoding="utf-8")
        ast.parse(source, filename=str(p))
        return "语法检查通过：未发现语法错误。"
    except SyntaxError as e:
        return f"语法错误：第 {e.lineno} 行，第 {e.offset} 列：{e.msg}"
    except Exception as e:
        return f"语法检查失败：{e}"


def run_ruff(path: str) -> str:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            return "Ruff 检查通过：未发现问题。"
        return output.strip() or f"Ruff 返回码：{result.returncode}"
    except FileNotFoundError:
        return "未安装 ruff，请运行 pip install ruff。"
    except subprocess.TimeoutExpired:
        return "Ruff 检查超时。"
    except Exception as e:
        return f"Ruff 检查失败：{e}"


def count_lines(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return f"错误：文件不存在 {path}"

    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    comments = sum(1 for line in lines if line.strip().startswith("#"))
    code = total - blank - comments

    return f"总行数：{total}，空行：{blank}，注释行：{comments}，代码行：{code}"


TOOL_MAP = {
    "read_file": read_file,
    "list_files": list_files,
    "run_syntax_check": run_syntax_check,
    "run_ruff": run_ruff,
    "count_lines": count_lines,
}


def execute_tool(name: str, args: dict) -> str:
    if name not in TOOL_MAP:
        return f"错误：未知工具 {name}"

    try:
        return TOOL_MAP[name](**args)
    except TypeError as e:
        return f"工具参数错误：{e}"
    except Exception as e:
        return f"工具执行失败：{e}"