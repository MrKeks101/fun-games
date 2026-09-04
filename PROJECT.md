# fun-games — Project & Workflow

## What this is

`fun-games` will be a website offering simple games playable against AI bots.

The end goal is a deployed site anyone can visit and play. The real goal is
learning: this project exists to build hands-on skills in backend design,
frontend design, AI/game-solving, game theory, CI/CD, and whatever else comes
up along the way.

**Local-first.** Games are built first as standalone Python + `pygame`
programs that run on the desktop. Only once a game works locally do we decide
how to bring it to the web.

This is a long-running solo project worked on across many sessions. This
document is the working agreement — how changes get made. Architecture and
roadmap live in their own docs, added when we need them.

## Principles

- **Learning over speed.** Prefer the approach that teaches something over the
  quickest hack. It's fine to do things "the proper way" even when overkill.
- **Local-first, web later.** Get it working on the desktop, then port.
- **Small, shippable steps.** Every change should leave `main` runnable.
- **Write it down.** Decisions with lasting impact get recorded (see
  [Decisions](#decisions)), so future sessions don't re-litigate them.
- **Green main.** `main` always passes the local test suite.

## Repository layout

```
/                repo root
README.md        public-facing blurb
PROJECT.md       this file — workflow & working agreement
pyproject.toml   pytest + coverage config
requirements.txt runtime + test dependencies
docs/            requirements, tickets, design notes, roadmap
  requirements/  PM's domain analysis and requirements per feature
  tickets/       PM's tickets for the dev agent
games/           one package per game (pygame apps)
tests/           local test suite (mirrors games/)
.claude/agents/  agent definitions (Project Manager, Developer)
```

## Local setup

```
python -m venv .venv
.venv\Scripts\activate            # PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the tests + coverage gate from the repo root:

```
pytest
```

(`pyproject.toml` wires in `--cov=games --cov-fail-under=90`.)

## Tech stack

- **Language:** Python 3.
- **Games:** `pygame` for rendering and input.
- **Tests:** `pytest`, run locally.
- **Web:** undecided. Chosen per game once it works locally, recorded as a
  decision below.

## Roles & agent workflow

Four roles. Two are AI agents; two are the human (Luiz).

### Project Manager (agent)

- Understands the domain of the feature or game (rules, edge cases, game
  theory where relevant).
- Writes requirements into `docs/requirements/<feature>.md`.
- Breaks the work into tickets in `docs/tickets/`, each small enough for one
  dev cycle, with clear acceptance criteria.
- Does **not** write production code.

### Developer (agent)

- Picks up a ticket and implements the feature or bug fix.
- Creates or updates the local test suite for **every** change — a feature
  ticket adds tests for the new behaviour; a bug ticket adds a failing test
  that reproduces the bug first.
- Runs the full local suite and only hands off when it passes.
- Reports back against the ticket's acceptance criteria.

### Stakeholder (human — Luiz)

- Owns the vision and priorities; decides what gets built and in what order.
- Clarifies domain questions the PM raises.

### QA (human — Luiz)

- Runs integration / exploratory testing on the running app (things automated
  local tests don't cover — feel, UX, real play against the bot).
- A feature is **only fully approved when Luiz says so.** No agent may mark a
  ticket done; the dev agent marks it "ready for QA".

### Flow

```
Stakeholder states a goal
      │
      ▼
Project Manager ── requirements ──▶ tickets (docs/tickets/)
      │
      ▼
Developer ── implement + tests ──▶ local suite passes ──▶ "ready for QA"
      │
      ▼
QA (Luiz) ── integration testing ──▶ approve │ send back with notes
      │
   approved
      ▼
   merged
```

## Git workflow

Feature branches with pull requests. `main` is protected in practice: no direct
commits.

### Branch naming

```
feat/<short-description>     new feature
fix/<short-description>      bug fix
chore/<short-description>    tooling, deps, config
docs/<short-description>     documentation only
refactor/<short-description> no behaviour change
```

### Cycle

1. Start from an up-to-date `main`: `git switch main && git pull`.
2. Create a branch: `git switch -c feat/tic-tac-toe-board`.
3. Make focused commits as you go.
4. Push and open a PR against `main`.
5. The local test suite must pass.
6. Self-review the PR diff — read every line as if someone else wrote it.
7. QA (Luiz) approves.
8. Merge (squash). Delete the branch.

Keep PRs small enough to review in one sitting. If a feature is large, split it
into sequential PRs (usually one per ticket).

### Commit messages

Conventional-commit style:

```
<type>: <imperative summary>

<optional body: what and why, not how>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`.

## Testing

- **Local only for now.** `pytest` run from the repo root, coverage via
  `pytest-cov`.
- **Coverage target: 90% line coverage** across the project. A change that
  drops coverage below 90% is not ready for QA. Measured with
  `pytest --cov=games --cov-report=term-missing --cov-fail-under=90`.
- New logic ships with tests. Game rules and AI move selection especially —
  cheap to test, expensive to get wrong.
- The dev agent creates or updates tests on every change; a bug fix starts
  with a failing test that reproduces the bug.
- Integration testing is manual, done by QA (Luiz) on the running app.

## CI/CD

Deferred. No hosted CI yet — tests run locally. CI (run the suite on every PR)
and CD (deploy on merge) get set up when the first game is heading to the web.

## Working cadence

Each working session:

1. Stakeholder picks one item and states the goal.
2. PM produces requirements + tickets.
3. Dev works tickets one at a time: branch, implement, test, PR.
4. QA tests and approves.
5. If a session ends mid-ticket, leave the branch pushed with a note in the PR
   describing what's left.

Larger direction (what to build next) is tracked in `docs/roadmap.md` once it
exists; until then, decided at the start of each session.

## Decisions

A running log of choices that outlive a single session. Newest first.

| Date       | Decision                                              | Why |
|------------|-------------------------------------------------------|-----|
| 2026-09-04 | Games built local-first as Python + pygame apps       | Focus on game/AI logic before web concerns |
| 2026-09-04 | Two-agent workflow: PM writes tickets, Dev implements | Practice requirements → tickets → dev handoff |
| 2026-09-04 | Luiz is Stakeholder + QA; only Luiz approves a feature | Human owns priorities and final sign-off |
| 2026-09-04 | Local `pytest` only; CI/CD deferred to first web port | No web infra needed yet |
| 2026-09-04 | 90% line-coverage target, enforced with `--cov-fail-under=90` | Objective, simple quality bar |
| 2026-09-04 | Feature-branch + PR workflow, squash merge            | Build PR/review habits; keep history clean |
| 2026-09-04 | Web stack deferred, decided per game                  | Avoid committing before we know the needs |
