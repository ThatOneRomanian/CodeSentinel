import json
import re
from typing import Any, Dict, List, Optional, Tuple

import yaml


def parse_json(content: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON content and return the parsed object."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def load_yaml_document(content: str) -> Optional[Dict[str, Any]]:
    """
    Load YAML content with safe_load, returning a dict only when the document
    represents a mapping at the top level.
    """
    try:
        parsed = yaml.safe_load(content)
        if isinstance(parsed, dict):
            return parsed
    except yaml.YAMLError:
        pass
    return None


def _find_yaml_key_line(content: str, key_name: str) -> int:
    """
    Find the first line number where the top-level key appears.
    """
    pattern = re.compile(rf"^(\s*){re.escape(key_name)}\s*:", re.IGNORECASE)
    for i, line in enumerate(content.splitlines()):
        if pattern.match(line):
            return i + 1
    return 1  # Fallback to start of file if we cannot locate the key


def get_yaml_key_value(content: str, key_name: str) -> Optional[Tuple[str, int]]:
    """
    Attempt to read a top-level YAML key's value and return the string value
    along with the line number where the key is defined.
    """
    parsed = load_yaml_document(content)
    if not parsed or key_name not in parsed:
        return None

    raw_value = parsed[key_name]
    if isinstance(raw_value, (dict, list)):
        return None

    value = str(raw_value).strip()
    line_number = _find_yaml_key_line(content, key_name)
    return value, line_number


def parse_dockerfile(content: str) -> List[Tuple[str, str, int]]:
    """
    Parses a Dockerfile into a list of (instruction, argument, line_number).
    Handles comments, blank lines, and backslash continuations.
    """
    instructions: List[Tuple[str, str, int]] = []
    pending = ""
    pending_line = 0

    for i, raw_line in enumerate(content.splitlines()):
        line_num = i + 1
        line = raw_line.rstrip()

        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if pending:
            pending += " " + line.strip()
        else:
            pending = line.strip()
            pending_line = line_num

        if pending.endswith("\\"):
            pending = pending[:-1].strip()
            continue

        match = re.match(r"^([A-Z]+)\s+(.*)$", pending, re.IGNORECASE)
        if match:
            instruction = match.group(1).upper()
            arguments = match.group(2).strip()
            instructions.append((instruction, arguments, pending_line))
        pending = ""
        pending_line = 0

    return instructions


def find_hcl_blocks(
    content: str, block_type: str, block_name: Optional[str] = None
) -> List[Tuple[str, int]]:
    """
    Finds top-level HCL blocks matching the provided block_type and optional
    block_name using a simple brace counting approach.
    """
    blocks: List[Tuple[str, int]] = []
    header_pattern = (
        rf'^\s*{re.escape(block_type)}\s+"{re.escape(block_name)}"\s+"[^"]*"\s*\{{'
        if block_name
        else rf'^\s*{re.escape(block_type)}\s+"[^"]*"\s*(?:"[^"]*")?\s*\{{'
    )
    lines = content.splitlines()
    collecting = False
    brace_depth = 0
    block_lines: List[str] = []
    start_line = 0

    for i, line in enumerate(lines):
        if not collecting:
            if re.match(header_pattern, line, re.IGNORECASE):
                collecting = True
                brace_depth = line.count("{") - line.count("}")
                block_lines = [line]
                start_line = i + 1
                if brace_depth <= 0:
                    blocks.append(("\n".join(block_lines), start_line))
                    collecting = False
            continue

        block_lines.append(line)
        brace_depth += line.count("{") - line.count("}")
        if brace_depth <= 0:
            blocks.append(("\n".join(block_lines), start_line))
            collecting = False

    return blocks