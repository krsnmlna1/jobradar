# learning — cabang career

Workspace untuk Employment Action Plan (Phase 0–6). Cabang audit terpisah di `~/audits/`.
Tracker + dokumennya di vault Obsidian `D:/Trinity` → `02-Career/`.

## Env: uv — sudah dipatenkan

Dipilih 27 Agu 2026. Master doc minta pilih satu dan konsisten. **Jangan gonta-ganti** ke
`venv`, `poetry`, `conda`, atau `pip install` global.

Satu venv untuk seluruh cabang, di `~/learning/.venv`. Semua subfolder ikut venv ini —
`uv` manjat ke atas nyari `pyproject.toml` terdekat dan ketemunya di root sini.

```bash
uv run python script.py     # jalan dari subfolder mana pun
uv run pytest
uv run ruff check .
```

Nggak perlu `source .venv/bin/activate`. Kalau butuh venv-nya kebaca editor, arahin
interpreter ke `~/learning/.venv/bin/python`.

## Nambah dependency

```bash
uv add httpx                              # ke workspace root
uv add --group dev mypy                   # tooling
uv add --package career-hello httpx       # ke satu member doang
```

## Nambah project baru

```bash
uv init --package software/api            # bikin member baru
```

Terus daftarin di `members` pada `pyproject.toml` root, dan:

```bash
uv sync --all-packages
```

> ⚠️ **`--all-packages`, bukan `uv sync` polos.** Root ini `package = false`, jadi `uv sync`
> biasa cuma masang dependency root dan nggak masang member workspace-nya.

## Struktur

```text
~/learning/
├── pyproject.toml     # workspace root, virtual (package = false)
├── .venv/             # SATU venv untuk semua
├── software/
│   └── python/        # member: career-hello (Phase 0 smoke test)
│       api/ backend/ database/ testing/
├── automation/        # Phase 2
├── ai/                # Phase 3
├── security/          # Phase 4
└── infrastructure/    # Phase 5
```

Folder dipecah per **domain skill**, bukan per job title — job itu hasil kombinasi skill.

## Smoke test

```bash
uv run career-hello
```

Kalau ini jalan dari clean clone tanpa aktivasi manual, env-nya beres. Itu exit criteria
Phase 0.
