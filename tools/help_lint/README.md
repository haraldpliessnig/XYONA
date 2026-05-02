# Operator Help Lint

Run from the XYONA workspace root:

```bash
python tools/help_lint/operator_help_lint.py --workspace .
```

The linter is strict by default. It validates every current public Core, CDP,
and Lab operator against `OPERATOR_HELP_STANDARD.md`.
