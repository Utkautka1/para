## 📝 Description

Please provide a concise summary of the changes and the architectural motivation.

---

## 🎯 Type of Change

- [ ] 🚀 New feature (non-breaking change adding functionality)
- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] 🔒 Security hardening (vulnerability mitigation or secret protection)
- [ ] ♻️ Architecture refactor (code quality or module decomposition)
- [ ] 📚 Documentation update (UML or engineering specifications)
- [ ] ⚙️ CI/CD & tooling improvements

---

## ✅ Quality Checklist

- [ ] **Function Length**: All new or modified functions/methods are strictly **$\le 25$ lines** and adhere to Single Responsibility.
- [ ] **Tests**: New unit or integration tests have been added. All tests pass (`make test`).
- [ ] **Linter & Security**: Passed `ruff check .`, `ruff format .`, and `bandit` AST analysis (`make lint`).
- [ ] **Secrets & Hygiene**: Passed `pre-commit run --all-files` (zero leaked tokens or passwords).
- [ ] **UML Architecture**: Updated [`docs/UML.md`](docs/UML.md) diagrams for any modified or added domain models or services.
- [ ] **Zero Documentation Drift**: Synchronized specifications via `make docs` and verified with `make docs-check`.
