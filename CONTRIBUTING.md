# Contributing

## Branch policy

Primary protected branch in this repository is `houshmand`.

Rules:
1. **Do not push directly to `houshmand`.**
2. Create a feature branch for each task (`feature/*`, `fix/*`, `lumi/*`, etc.).
3. Open a Pull Request into `houshmand`.
4. Merge via PR only after review/checks.

## Recommended local workflow

```bash
# sync base branch
git checkout houshmand
git pull origin houshmand

# create work branch
git checkout -b feature/my-change

# do work, then commit
git add .
git commit -m "feat: <short description>"

# push branch
git push -u origin feature/my-change

# open PR -> base: houshmand
```

## Commit style

Use concise commit prefixes where possible:
- `feat:` new functionality
- `fix:` bugfix
- `chore:` maintenance
- `docs:` documentation
- `refactor:` internal improvements without behavior change
