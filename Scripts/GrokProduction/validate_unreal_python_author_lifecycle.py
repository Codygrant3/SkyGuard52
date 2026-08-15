from __future__ import annotations

import ast
import sys
from pathlib import Path


def line(node: ast.AST) -> int:
    return int(getattr(node, "lineno", 0))


def is_quit_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
        return False
    function = node.value.func
    return isinstance(function, ast.Attribute) and function.attr == "quit_editor"


def is_unconditional_raise(node: ast.AST) -> bool:
    return isinstance(node, ast.Raise)


def validate(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    issues: list[str] = []
    for parent in ast.walk(tree):
        body = getattr(parent, "body", None)
        if not isinstance(body, list):
            continue
        for index, statement in enumerate(body[:-1]):
            if not isinstance(statement, ast.If):
                continue
            if not any(is_quit_call(child) for child in statement.body):
                continue
            next_statement = body[index + 1]
            success_branch_terminates = bool(statement.body and isinstance(statement.body[-1], (ast.Return, ast.Raise)))
            has_else = bool(statement.orelse)
            if is_unconditional_raise(next_statement) and not success_branch_terminates and not has_else:
                issues.append(
                    f"{path}:{line(statement)} success quit path falls through to unconditional raise at line {line(next_statement)}"
                )
    return issues


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate_unreal_python_author_lifecycle.py <author.py> [<author.py> ...]", file=sys.stderr)
        return 2
    issues: list[str] = []
    for raw in argv[1:]:
        path = Path(raw)
        if not path.is_file():
            issues.append(f"missing author: {path}")
            continue
        issues.extend(validate(path))
    if issues:
        print("FAILED_UNREAL_PYTHON_AUTHOR_LIFECYCLE")
        for issue in issues:
            print(issue)
        return 1
    print("PASS_UNREAL_PYTHON_AUTHOR_LIFECYCLE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
