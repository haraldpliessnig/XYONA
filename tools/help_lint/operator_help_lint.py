#!/usr/bin/env python3
"""Validate XYONA public operator help against OPERATOR_HELP_STANDARD.md."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment dependency
    print("PyYAML is required: pip install PyYAML", file=sys.stderr)
    raise SystemExit(2) from exc


REQUIRED_LOCALES = ("en", "de")
STANDARD = "operator_help_v1"
MAX_SHORT_LENGTH = 180
FORBIDDEN_SHORT_FRAGMENTS = (
    "descriptor",
    "host-contract",
    "host contract",
    "fixture",
    " workflow",
    "-workflows",
    "operator for",
    "operator fuer",
    "schema",
)
SECTION_ORDER = [
    "Tech Sheet",
    "Process",
    "Ports",
    "Parameters",
    "Data",
    "Application",
    "Processing Modes",
    "Requirements",
    "Detailed Technical Description",
    "Provenance",
    "Tips",
    "See Also",
]
NON_TRANSLATABLE_KEYS = [
    "standard",
    "id",
    "tags",
    "provider",
    "family",
    "operator",
    "capability",
    "availability",
    "process_shape",
    "domain",
    "related",
    "since",
]


@dataclass(frozen=True)
class OperatorSpec:
    repo: str
    path: Path
    data: dict[str, Any]
    docs: dict[str, Path]


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, path: Path, message: str) -> None:
        self.errors.append(f"{path}: {message}")


def load_yaml(path: Path, validation: Validation) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        validation.error(path, f"cannot parse YAML: {exc}")
        return None
    if not isinstance(data, dict):
        validation.error(path, "YAML document must be a mapping")
        return None
    return data


def load_yaml_documents(path: Path, validation: Validation) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            docs = [doc for doc in yaml.safe_load_all(handle) if doc is not None]
    except (OSError, yaml.YAMLError) as exc:
        validation.error(path, f"cannot parse YAML: {exc}")
        return []
    result: list[dict[str, Any]] = []
    for index, doc in enumerate(docs, start=1):
        if isinstance(doc, dict):
            result.append(doc)
        else:
            validation.error(path, f"document {index} must be a mapping")
    return result


def parse_markdown(path: Path, validation: Validation) -> tuple[dict[str, Any], str] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        validation.error(path, f"cannot read Markdown: {exc}")
        return None
    if not text.startswith("---\n"):
        validation.error(path, "frontmatter must start on line 1")
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        validation.error(path, "frontmatter closing delimiter is missing")
        return None
    raw = text[4:end]
    try:
        frontmatter = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        validation.error(path, f"invalid frontmatter YAML: {exc}")
        return None
    if not isinstance(frontmatter, dict):
        validation.error(path, "frontmatter must be a mapping")
        return None
    return frontmatter, text[end + 5 :]


def collect_specs(workspace: Path, validation: Validation) -> list[OperatorSpec]:
    specs: list[OperatorSpec] = []
    for repo in ("xyona-core", "xyona-cdp-pack"):
        root = workspace / repo
        for path in sorted((root / "src" / "operators").rglob("op.yaml")):
            data = load_yaml(path, validation)
            if data is None:
                continue
            docs = {locale: path.parent / "docs" / f"{locale}.md" for locale in REQUIRED_LOCALES}
            specs.append(OperatorSpec(repo=repo, path=path, data=data, docs=docs))

    lab_path = workspace / "xyona-lab" / "specs" / "operators" / "lab-public.op.yaml"
    if lab_path.exists():
        for data in load_yaml_documents(lab_path, validation):
            module = str(data.get("moduleName") or str(data.get("id", "")).split(".")[-1])
            docs = {
                locale: workspace / "xyona-lab" / "docs" / "help" / "lab" / locale / "operators" / f"{module}.md"
                for locale in REQUIRED_LOCALES
            }
            specs.append(OperatorSpec(repo="xyona-lab", path=lab_path, data=data, docs=docs))
    return specs


def capability(spec: dict[str, Any]) -> list[str]:
    caps = spec.get("capabilities") if isinstance(spec.get("capabilities"), dict) else {}
    engine = spec.get("engine") if isinstance(spec.get("engine"), dict) else {}
    result: list[str] = []
    if caps.get("canRealtime"):
        result.append("rt")
    if caps.get("canHQ"):
        result.append("hq")
    if engine.get("materialization") in {"spectral_data", "control_data", "report", "file_collection"}:
        result.append("data")
    if engine.get("wholeFileRequired") or engine.get("lengthChanging"):
        result.append("offline")
    return result or ["offline"]


def availability(tokens: Iterable[str]) -> str:
    token_set = set(tokens)
    rt = "rt" in token_set
    hq = "hq" in token_set
    data = "data" in token_set
    offline = "offline" in token_set
    if rt and hq and data:
        return "insertable_rt_hq_data"
    if rt and hq:
        return "insertable_rt_hq"
    if rt:
        return "insertable_rt"
    if hq and data:
        return "insertable_data_hq"
    if hq:
        return "insertable_hq"
    if data:
        return "insertable_data"
    if offline:
        return "insertable_offline"
    return "unavailable"


def port_ids(spec: dict[str, Any]) -> list[str]:
    ports = spec.get("ports") if isinstance(spec.get("ports"), dict) else {}
    result: list[str] = []
    for direction in ("inputs", "outputs"):
        entries = ports.get(direction, [])
        if isinstance(entries, list):
            result.extend(str(port.get("id")) for port in entries if isinstance(port, dict) and port.get("id"))
    return result


def param_ids(spec: dict[str, Any]) -> list[str]:
    params = spec.get("params", [])
    if not isinstance(params, list):
        return []
    return [str(param.get("id")) for param in params if isinstance(param, dict) and param.get("id")]


def h2_sections(body: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"^## (.+)$", body, flags=re.MULTILINE)]


def first_h1_and_prose(body: str) -> tuple[str, str]:
    lines = body.splitlines()
    h1_index = -1
    title = ""
    for index, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            h1_index = index
            title = line[2:].strip()
            break
    if h1_index < 0:
        return "", ""
    for line in lines[h1_index + 1 :]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            return title, ""
        return title, stripped
    return title, ""


def section_body(body: str, section: str) -> str:
    match = re.search(rf"^## {re.escape(section)}\n(.*?)(?=^## |\Z)", body, flags=re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def validate_frontmatter(
    spec_record: OperatorSpec,
    locale: str,
    path: Path,
    frontmatter: dict[str, Any],
    body: str,
    validation: Validation,
) -> None:
    spec = spec_record.data
    operator_id = str(spec.get("id", ""))
    provider = str(spec.get("provider", ""))
    family = str(spec.get("family", ""))
    engine = spec.get("engine") if isinstance(spec.get("engine"), dict) else {}
    expected = {
        "standard": STANDARD,
        "id": f"help.node.{operator_id}",
        "provider": provider,
        "family": family,
        "operator": operator_id,
        "capability": capability(spec),
        "availability": availability(capability(spec)),
        "process_shape": engine.get("processShape"),
        "domain": engine.get("domain"),
        "since": str(spec.get("version", "0.1.0")),
    }
    for key, expected_value in expected.items():
        if frontmatter.get(key) != expected_value:
            validation.error(path, f"frontmatter {key!r} must be {expected_value!r}, got {frontmatter.get(key)!r}")

    for key in ("title", "short"):
        value = frontmatter.get(key)
        if not isinstance(value, str) or not value.strip():
            validation.error(path, f"frontmatter {key!r} must be a non-empty string")

    short = frontmatter.get("short")
    if isinstance(short, str):
        if len(short) > MAX_SHORT_LENGTH:
            validation.error(path, f"frontmatter 'short' must be {MAX_SHORT_LENGTH} characters or less")
        lower_short = short.lower()
        for fragment in FORBIDDEN_SHORT_FRAGMENTS:
            if fragment in lower_short:
                validation.error(
                    path,
                    f"frontmatter 'short' must be application-focused and must not contain {fragment!r}",
                )

    tags = frontmatter.get("tags")
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        validation.error(path, "frontmatter 'tags' must be a string list")
    else:
        for tag in ("node", provider, family):
            if tag and tag not in tags:
                validation.error(path, f"frontmatter 'tags' must include {tag!r}")

    related = frontmatter.get("related")
    if not isinstance(related, list) or any(not isinstance(item, str) for item in related):
        validation.error(path, "frontmatter 'related' must be a string list")

    h1, first_prose = first_h1_and_prose(body)
    if not h1:
        validation.error(path, "exactly one H1 title is required")
    elif frontmatter.get("title") != h1:
        validation.error(path, "frontmatter title must match H1")
    if short != first_prose:
        validation.error(path, "frontmatter short must match the first prose line under H1")


def validate_body(spec_record: OperatorSpec, path: Path, body: str, validation: Validation) -> None:
    spec = spec_record.data
    sections = h2_sections(body)
    if sections != SECTION_ORDER:
        validation.error(path, f"H2 sections must be {SECTION_ORDER}, got {sections}")

    port_section = section_body(body, "Ports")
    documented_ports = re.findall(r"^- \*\*ID:\*\* `([^`]+)`", port_section, flags=re.MULTILINE)
    expected_ports = port_ids(spec)
    if documented_ports != expected_ports:
        validation.error(path, f"documented port IDs must be {expected_ports}, got {documented_ports}")

    param_section = section_body(body, "Parameters")
    documented_params = re.findall(r"^- \*\*ID:\*\* `([^`]+)`", param_section, flags=re.MULTILINE)
    expected_params = param_ids(spec)
    if expected_params:
        if documented_params != expected_params:
            validation.error(path, f"documented parameter IDs must be {expected_params}, got {documented_params}")
    elif "No user parameters." not in param_section and "Keine Benutzerparameter." not in param_section:
        validation.error(path, "parameterless operators must state that there are no user parameters")


def validate_locale_parity(
    docs: dict[str, tuple[Path, dict[str, Any], str]],
    validation: Validation,
) -> None:
    baseline_locale = REQUIRED_LOCALES[0]
    if baseline_locale not in docs:
        return
    base_path, base_fm, base_body = docs[baseline_locale]
    base_sections = h2_sections(base_body)
    for locale in REQUIRED_LOCALES[1:]:
        if locale not in docs:
            continue
        path, frontmatter, body = docs[locale]
        for key in NON_TRANSLATABLE_KEYS:
            if frontmatter.get(key) != base_fm.get(key):
                validation.error(path, f"frontmatter {key!r} must match {base_path}")
        if h2_sections(body) != base_sections:
            validation.error(path, f"H2 section order must match {base_path}")


def validate_related_ids(
    docs_by_id: dict[str, list[Path]],
    docs: dict[str, tuple[Path, dict[str, Any], str]],
    validation: Validation,
) -> None:
    for path, frontmatter, _body in docs.values():
        related = frontmatter.get("related", [])
        if not isinstance(related, list):
            continue
        for item in related:
            if item not in docs_by_id:
                validation.error(path, f"related help id does not exist: {item}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="XYONA workspace root")
    args = parser.parse_args(argv)

    workspace = args.workspace.resolve()
    validation = Validation()
    specs = collect_specs(workspace, validation)
    docs_by_id: dict[str, list[Path]] = {}
    parsed_by_spec: list[dict[str, tuple[Path, dict[str, Any], str]]] = []

    for spec_record in specs:
        parsed_docs: dict[str, tuple[Path, dict[str, Any], str]] = {}
        for locale in REQUIRED_LOCALES:
            path = spec_record.docs[locale]
            if not path.exists():
                validation.error(path, f"missing required {locale} operator help file")
                continue
            parsed = parse_markdown(path, validation)
            if parsed is None:
                continue
            frontmatter, body = parsed
            parsed_docs[locale] = (path, frontmatter, body)
            help_id = frontmatter.get("id")
            if isinstance(help_id, str):
                docs_by_id.setdefault(help_id, []).append(path)
            validate_frontmatter(spec_record, locale, path, frontmatter, body, validation)
            validate_body(spec_record, path, body, validation)
        parsed_by_spec.append(parsed_docs)

    for parsed_docs in parsed_by_spec:
        validate_locale_parity(parsed_docs, validation)
        validate_related_ids(docs_by_id, parsed_docs, validation)

    for error in validation.errors:
        print(f"error: {error}", file=sys.stderr)
    if validation.errors:
        print(f"operator help lint failed: {len(validation.errors)} error(s)", file=sys.stderr)
        return 1
    print(f"operator help lint passed: {len(specs)} operator(s), locales: {', '.join(REQUIRED_LOCALES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
