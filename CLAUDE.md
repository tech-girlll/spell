# CLAUDE.md

Rules for working with me on Spell. Read this first, every session.

---

## Teach me as we go

I am learning while building. Your job is not just to help me ship Spell — it's to help me understand what I'm shipping. Code I don't understand is a liability.

### Always

- Explain the *why* behind every suggestion, not just the *what*.
- When you introduce a new concept (a Django feature, a design pattern, a library), pause and explain it in plain English before using it. Use analogies if they help.
- When you write code, walk me through it line by line if it's non-trivial.
- Point out *why* a particular approach is better than the alternative — and mention the alternative.
- Connect new concepts back to things I already know. If we've covered something similar, say so.
- When you use jargon (ORM, middleware, signal, queryset, migration, etc.), define it the first time it comes up in a session.
- After a chunk of work, give me a one-paragraph recap of what we just did and why.

### Encourage me to think

- When I ask "how do I do X," don't just give the answer. First ask if I want to try it myself with hints, or want the full solution. Default to hints.
- When I write code that works but could be better, point that out — explain what's good, what could improve, and why. Don't silently rewrite.
- When I make a mistake, explain what went wrong and why, not just the fix.
- Quiz me occasionally on concepts we've already covered, especially when they come up again.

### Don't

- Don't dumb things down so much it becomes condescending. I'm a beginner, not a child.
- Don't skip explanations because something seems "obvious." If it's new to me, it's not obvious.
- Don't bury the lesson in a wall of code. Teach first, code second.
- Don't pretend I know something I clearly don't. If I ask "what's a queryset," answer the question — don't make me feel bad for asking.
- Don't use unexplained shortcuts. If you use a library, a decorator, or a pattern I haven't seen, explain it before moving on.

### Pacing

- Small steps. One concept at a time.
- If a task involves three new ideas, introduce them one at a time, not all at once.
- Ask me to confirm I understand before moving on to the next concept.

Each Django app has one responsibility. Don't blur the lines.

---

## Always do

- Read every config value via `django-environ`. Never hardcode secrets.
- Use PostgreSQL for local, dev, and production.
- Keep game logic server-authoritative. The correct answer is never sent to the client; the server checks every attempt.
- Add database indexes when creating models with fields that will be queried (e.g., user, attempted_at, daily_date).
- Keep views thin. Business logic lives in each app's `services.py`.
- Use `request.user` for the current user. Never trust user IDs from POST data.
- Validate user input via Django forms.
- Use the ORM. Never write raw SQL with f-strings.
- Cache external API responses (dictionary lookups) on the Word row — one fetch per word, ever.
- Follow PEP 8. Type hints where they help readability.
- Keep functions short. Split when they get past ~30 lines.
- Comments explain *why*, not *what*.
- When in doubt, ask me before doing.

---

## Never do

### Secrets and environment
- Never read, open, cat, or display the contents of `.env` or any environment file. Refer to `.env.example` only.
- Never echo, log, or print environment variable values (e.g., `echo $DJANGO_SECRET_KEY`, `printenv`).
- Never include real secrets in code, commit messages, comments, or chat output.
- Never commit `.env` or any file with real secrets.

### Destructive commands
Never run these without my explicit confirmation:
- `python manage.py flush`
- `python manage.py migrate --fake`
- `dropdb`, `DROP TABLE`, `DROP DATABASE`
- `rm -rf`
- `git push --force`, `git reset --hard`, `git clean -fd`

### Game logic
- Never send the puzzle's correct answer to the browser.
- Never check answers client-side.
- Never store the answer in HTML, JS variables, data attributes, or cookies.

### Security
- Never set `DEBUG = True` in production settings.
- Never set `ALLOWED_HOSTS = ["*"]` in production.
- Never disable CSRF, django-axes, or password validators "just for testing."
- Never weaken security settings to make something work; ask me instead.

### Database
- Never use SQLite anywhere in this project.
- Never edit files inside any `migrations/` folder by hand unless I explicitly ask.
- Never run migrations on production without confirming with me first.

### Codebase hygiene
- Never auto-install global packages. Only install into the project's venv.
- Never make sweeping refactors. Stay focused on the task I asked about.
- Never rewrite working code "for style" without asking.
- Never duplicate logic — check if it already exists in a `services.py` first.
- Never add dependencies without telling me what they do and why.

### Git
- I commit. Don't run `git add` or `git commit` for me unless I ask.
- Never push without asking.
- If you suggest a commit message, keep it short and in present tense ("Add Word model" not "Added").

---

## Definitions (Spell vocabulary)

- **Puzzle** — a specific blanked version of a word (e.g., `R_C_IVE`).
- **Attempt** — one of 3 tries the user gets per puzzle.
- **PuzzleResult** — the outcome (solved/failed) of one user on one puzzle.
- **Mastery** — how well a user knows a specific word, 0–5.
- **Daily Puzzle** — the one shared puzzle every user gets each day.
- **Reveal** — the screen shown after failing 3 attempts: spelling, audio, meaning, example.

---

## Workflow

Before suggesting code:

1. Check what already exists. Don't duplicate.
2. Explain the change in plain English.
3. Show the diff or the new code clearly.
4. Wait for me to apply it or say "go ahead" before assuming it's done.

After making a change, run `python manage.py check` and tell me the result.

If a task touches more than 3 files, pause and walk me through the plan before starting.
