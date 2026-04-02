111# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Apps

**CLI version:**
```bash
python3 quiz_app.py
```

**Web version:** Open `quiz_app_web.html` directly in a browser — no server or build step needed.

There are no automated tests, no linter configuration, and no external dependencies.

## Architecture

This repo contains two independent implementations of the same quiz app:

### CLI (`quiz_app.py`)
- All question data lives in the `QUESTIONS` dict at the top of the file (3 categories, ~7-8 questions each, keyed by category name).
- `QuestionTimer` is a `threading.Thread` subclass that runs a countdown in the background and sets a `time_up` flag when it expires. `ask_question()` polls this flag after each `input()` call.
- Core flow: `main()` → `show_main_menu()` → `choose_category()` → `load_questions()` (shuffles and picks 5) → `run_quiz()` (loops `ask_question()`) → `show_results()`.
- Constants at module level: `TIME_LIMIT = 15` (seconds), `SEPARATOR`.

### Web (`quiz_app_web.html`)
- Single self-contained HTML file: inline CSS + inline JS, no external JS framework.
- UI is a set of `<section>` elements with IDs (`s-welcome`, `s-menu`, `s-quiz`, `s-results`, etc.); `goTo(id)` hides all and shows the target.
- Question data is in the `CATS` JS array (same 3 categories; answer stored as 0-based index into `opts` array, unlike the CLI's letter-based answer).
- Auth is fully client-side using `localStorage`: `qz_users` stores user records (passwords stored **plaintext** — this is intentional for a demo), `qz_sess` stores the current session.
- The "2FA" flow generates a 6-digit code and displays it on screen — no email is actually sent.
- Timer in the web version uses `setInterval`; `runQuiz()` drives the question loop.
- Grade thresholds defined in the `GRADES` array: 100% / ≥80% / ≥60% / ≥40% / below 40%.
- Key constants in JS: `TIME_LIMIT = 15`, `NUM_Q = 5`.

## Modifying Questions

To add/edit questions in the CLI, update the `QUESTIONS` dict in `quiz_app.py`. Each entry:
```python
{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A"}
```

For the web version, update the `CATS` array in `quiz_app_web.html`. Each entry:
```js
{q: "...", opts: ["...", "...", "...", "..."], ans: 0}  // ans is 0-based index
```
