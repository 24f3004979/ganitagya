# PROJECT_CONTEXT.md

> Last updated: 2026-09-21. Status: **pre-v1 prototype**. Components exist separately; nothing is wired end to end yet.

## 0. Instructions for reading this document

- Treat sections marked **DECIDED** as fixed unless the author says otherwise.
- Treat sections marked **PROPOSED** as suggestions that still need the author's confirmation.
- Treat anything marked **UNKNOWN** as a question to ask, not something to invent.
- File paths marked *(inferred)* were deduced from import statements, not seen directly.
- Files **not yet shared** with the assistant: `server/service/mool.py`, `server/service/prashna_template.py` (defines `TEMPLATES`), `server/service/__init__.py` (defines `RootConceptGraph`), `server/exceptions.py`, `server/dev_log.py`, the web framework entrypoint, and DB config. Do not assume their contents beyond what is stated here.
- Code comments and naming in this repo are informal and mix English with Sanskrit terms. See the glossary.

## 1. What this project is

An adaptive learning application, currently scoped to foundational math. Three ideas work together:

1. A **root concept graph**: topics (for example "Basic Arithmetic", "Variable") linked by prerequisite edges. It is shared by all students.
2. **Siddhi**, an adaptive testing engine. It generates questions for a target topic, raises or lowers difficulty based on the student's answers, and walks *down* the graph to prerequisite topics when a student struggles. At the end it produces a report that updates the student's knowledge state.
3. **Chintan**, a front-end tool that shows a student an arithmetic expression being broken down one operation at a time, with an optional block animation (piles, groups) for each step. It is for understanding how an expression resolves, not for grading.

Target audience is not stated. The block view only supports whole numbers 0 to 100, which suggests early learners *(inferred)*.

## 2. Glossary

| Term | Meaning in this project |
|---|---|
| **Chintan** (चिंतन, contemplation) | Front-end expression-breakdown tool plus its TypeScript engine `ExpressionEngine` |
| **Siddhi** (सिद्धि, accomplishment) | Adaptive testing engine; owns difficulty adaptation and session reports |
| **Prashna** (प्रश्न, question) | Question generator that turns a `QuestionTemplate` into an expression string |
| **Mool** (मूल, root) | Per-student graph object derived from the root graph (author's term: "Student Mool graph"). Planned home: `server/service/mool.py` |
| **Root graph / ConceptGraph** | The shared prerequisite DAG of topics |
| **Component** | In Chintan, one resolved operation (`2*2`) given a tag (`component_0`) that later steps can reference |
| **Frontier** | Topics a student has not mastered whose prerequisites are all mastered: the natural "learn/test next" set |
| **Overlay** | A student's mastery data attached to root-graph node IDs. The root graph is never copied per student |
| **downgrade_concept(t)** | Returns the direct *prerequisites* of `t` (one hop) |
| **upgrade_concept(t)** | Returns the direct *dependents* of `t` (one hop) |

## 3. Architecture

```
FRONT END (Vue 3 + TypeScript + Tailwind v4)
  Login / Dashboard (student graph) / Session page
  Chintan component (ExpressionEngine + block canvas)
        |  HTTP + JWT
        v
API LAYER (Python; framework not stated, FastAPI assumed with SQLModel)
        |
        v
SERVICES
  GraphSyncService   runs the loop, applies reports          [to build]
  TopicRanker        picks what to test next                 [to build]
  StudentGraphView   root + overlay, frontier, blocked       [to build]  (the "Mool" object)
  SiddhiEngine       question adaptation, session report     [exists, needs fixes]
  Prashna            question generation                     [exists, needs fixes]
  RootGraphRepo      load/freeze/version the root graph      [to build]
  ConceptGraph       pure DAG structure (networkx DiGraph)   [exists, needs fixes]
        |
        v
POSTGRESQL (SQLModel / SQLAlchemy, JSONB for flexible state)
```

**Stack** (from imports): Python, `networkx`, `sqlmodel`, `sqlalchemy` (Postgres JSONB), `matplotlib` (graph drawing, to be moved out of server code). Front end: Vue 3 `<script setup lang="ts">`, Tailwind v4, HTML canvas. Chintan engine is TypeScript.

## 4. Component inventory

| Component | Path | Status | Responsibility |
|---|---|---|---|
| `ConceptGraph` | *(inferred)* `server/service/...` exported as `RootConceptGraph` | Works, has issues (section 9) | Topic nodes, prerequisite edges, cycle protection, one-hop traversal, drawing |
| `SiddhiEngine` | *(inferred)* `server/service/siddhi.py` | Works in isolation, unsafe for web use | Generates question batches per topic and level, adapts on previous result, switches to a prerequisite topic when the student fails |
| `Prashna`, `QuestionTemplate`, `topics` | `server/service/prashna.py` | Works, has bugs | Generates one expression string from a template |
| `TEMPLATES` | `server/service/prashna_template.py` | **UNKNOWN contents** | Dict: topic name to `QuestionTemplate` |
| Mool | `server/service/mool.py` | **UNKNOWN contents** | Intended student graph object |
| `ExpressionEngine` | `chintan/src/Arithmatic.ts` | Works for flat expressions | Splits an expression into ordered components |
| Chintan view | Vue SFC, path *(inferred)* three levels below the repo root, imports `../../../chintan/src/Arithmatic.ts` | Works, but one 800-line file | UI, step animation, block scenes, canvas renderer |
| User / Student models | none yet | Designed only | See section 5 |

## 5. Data model (PROPOSED, mostly DECIDED in principle)

```python
class Role(str, Enum):
    student = "student"
    admin = "admin"

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)   # incremental
    name: str
    email: str = Field(unique=True, index=True)              # future mailing
    password_hash: str                                       # argon2 or bcrypt, never returned by any API
    role: Role = Role.student

class StudentProfile(SQLModel, table=True):                  # 1:1 with User
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    root_graph_version: str
    siddhi_state: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))

class TopicMastery(SQLModel, table=True):                    # queryable overlay
    student_id: int = Field(foreign_key="user.id", primary_key=True)
    topic_id: str = Field(primary_key=True)                  # stable slug
    mastery: float = 0.0
    confidence: float = 0.0
    attempts: int = 0
    last_tested_at: datetime | None = None

class MasteryEvent(SQLModel, table=True):                    # append-only audit log
    id: int | None = Field(default=None, primary_key=True)
    report_id: str = Field(index=True, unique=True)          # idempotency key
    student_id: int = Field(foreign_key="user.id", index=True)
    payload: dict[str, Any] = Field(sa_column=Column(JSONB)) # the full SessionReport
    created_at: datetime

class SiddhiSession(SQLModel, table=True):                   # one adaptive test run
    id: str = Field(primary_key=True)                        # uuid
    student_id: int = Field(foreign_key="user.id", index=True)
    state: dict[str, Any] = Field(sa_column=Column(JSONB))   # target_topic, level, trace, pending questions + expected answers
    status: str                                              # active | finished
```

Rules: rows for anything you query ("who is weak on topic X"), JSONB for Siddhi's internal state and raw reports whose shape will change.

## 6. Design decisions

**DECIDED**

1. **Student is composition, not inheritance.** `User` + `StudentProfile` (1:1). A `Student` abstraction may exist in the service layer wrapping both. Reason: SQLModel and table inheritance are awkward, and it keeps graph data off the credentials row.
2. **The root graph is never copied per student.** It is shared, frozen at runtime, and versioned. A student's graph is `root + overlay`, computed on demand. New root topics appear as "unseen".
3. **`ConceptGraph` stays a pure structure.** No student logic inside it. Student logic lives in layers above it.
4. **Siddhi returns a report; it does not write to the graph.** The graph service applies the report. This makes Siddhi testable with stubs.
5. **Topic identity is a stable slug**, with display titles as node attributes. Mastery rows reference slugs, so renaming a topic must not orphan data.
6. **Reports carry an ID and are applied idempotently**, with an append-only event log so the mastery formula can be recomputed later.

**PROPOSED (confirm with the author)**

7. **Chintan is a teaching tool, not a test surface.** It currently reveals every step and the final answer client-side, so showing it during a graded question would leak the answer. Proposed use: after the student submits an answer, offer "show me how"; or a practice mode whose attempts are flagged as assisted.
8. **Answer checking is server-side.** The server stores the expected answer per generated question and never sends it to the client until the question is answered.
9. **v1 topic ranking** is a simple weighted score: low mastery, low confidence, staleness, plus a bonus for frontier topics. Keep it behind a `TopicRanker` interface so BKT, IRT or Elo can replace it later.

## 7. End-to-end flow (v1 target)

```
1. Student logs in                          POST /auth/login -> JWT
2. Dashboard loads student graph            GET  /me/graph        (root nodes + mastery + frontier)
3. Pick what to test                        GET  /me/next-topics  (TopicRanker over StudentGraphView)
4. Start a session on a topic               POST /sessions {topic}
      server: create SiddhiSession, generate batch of N questions,
              store expected answers, return [{question_id, expression}]
5. Student answers the batch                POST /sessions/{id}/answers
      server: evaluate answers, compute batch score, ask Siddhi to adapt:
              strong  -> raise level, same topic
              middle  -> same level
              weak    -> level 1 on a prerequisite topic (push current topic on trace)
      returns results plus next batch, or done=true
6. (Optional) Student opens Chintan on a question to see it broken down
7. Session ends                             Siddhi builds SessionReport
8. graph_service.apply_report(student, report)
      updates TopicMastery, appends MasteryEvent, flags prerequisites of failed topics
9. Dashboard refreshes                      GET /me/graph
```

## 8. Contracts

### 8.1 SessionReport (Siddhi to graph service)

```json
{
  "report_id": "uuid",
  "student_id": 1,
  "root_graph_version": "sha256:...",
  "started_at": "...",
  "ended_at": "...",
  "start_topic": "operation-order",
  "trace": ["operation-order", "basic-arithmetic"],
  "attempts": [
    {"topic": "operation-order", "level": 1, "expression": "2+3*4",
     "expected": "14", "given": "20", "correct": false, "time_ms": 8200}
  ]
}
```

### 8.2 Placeholder mastery update (PROPOSED, replace later)

For each topic in `attempts`: `score = correct / total` (optionally weighted by level); `mastery += 0.3 * (score - mastery)`; increment `attempts`; set `last_tested_at`. A topic counts as mastered at `mastery >= 0.7`. The 0.3 and 0.7 are placeholders.

### 8.3 Chintan-compatible expression

The Vue front end only accepts: `^\d+(\.\d+)?([+\-*/]\d+(\.\d+)?)*$` after stripping whitespace. That means digits, `+ - * /`, no brackets, no negatives, no variables. Any Siddhi question that should open in Chintan must satisfy this grammar until Chintan gains bracket support (see 11.3).

Chintan's engine output (positional tuple today): `[components_dictionary, component_list, final_expression]` where `components_dictionary = {"component_0": "2*2", "component_1": "2*2", "component_2": "component_0+component_1"}`. Precedence: `* /` first, then `+ -`, left to right. The engine only decomposes; it never computes a value. The Vue file evaluates the dictionary itself.

### 8.4 Topic identity

Every root-graph node id must be a slug and must have a matching entry in `TEMPLATES`, otherwise `SiddhiEngine` raises `KeyError` when it walks to that node. Seed topics currently defined in `prashna.py`: "Basic Arithmetic", "Variable", "Expression", "Operation Order", "Simplification" (slugs: `basic-arithmetic`, `variable`, `expression`, `operation-order`, `simplification`). **UNKNOWN**: the intended prerequisite edges between them.

## 9. Current-state findings (known issues)

### 9.1 `ConceptGraph`
1. `add_edge` silently creates missing nodes, so a typo makes a phantom topic. Require both nodes to exist.
2. Cycle check adds the edge, validates the whole graph, then reverts. Prefer checking `nx.has_path(self, topic, prerequisite)` first (and self-loops) before adding.
3. `add_dependencies` is not atomic: if the third prerequisite clashes, the first two remain.
4. Nodes are keyed by display name; use slugs plus attributes (`title`, `level`).
5. `downgrade_concept` and `upgrade_concept` are one hop only, and their names are ambiguous. Consider `prerequisites_of` and `unlocks`. `in_degree(topic)` raises on unknown nodes. Logging inside pure lookups is noise.
6. `draw()` imports matplotlib into server code. Move to a separate `viz` module. The comment on `rad=0` ("slightly curve") is wrong since `rad=0` is straight.
7. The shared graph instance is mutable. Freeze it (`nx.freeze`) after load.

### 9.2 `Prashna` / `SiddhiEngine`
1. **Shared templates are mutated.** `SiddhiEngine.generate` does `template.lower_bound -= ...` and `template.upper_bound += ...` on the object inside `TEMPLATES`. Bounds grow on every call, across every batch and every student. Fix: copy with `dataclasses.replace(template, ...)` and compute bounds from the original.
2. **Level 1 produces bracketed singletons.** `grouping = level`, so at level 1 `groups = 1` and each number becomes `(n)`, giving questions like `(4)+(7)`. Likely unintended.
3. **Grouping silently drops elements.** In `Prashna.generate`, `if len(group_member) < groups: break` discards leftovers. When variables are appended, the count is no longer divisible by `groups`, so a number or variable can vanish after shuffle.
4. **Dead branch.** `elif groups > 0:` after `if groups > 0:` can never run.
5. **Division by zero is possible.** Numbers come from `rnd.choices(range(start, end))` and `0` can land under `/`. Division is also not guaranteed exact, which conflicts with Chintan's block view (whole numbers, even division only).
6. **Negatives are bracketed** (`(-3)`), and lower bounds go negative quickly because of issue 1. Chintan rejects all brackets.
7. **`prev_response` convention** (`-1` both wrong, `0` one wrong, `1` both right) assumes pairs of questions, but `quantity` defaults to 3. Replace with a batch score, for example `>= 0.8` raise, `>= 0.4` hold, else lower (thresholds are placeholders).
8. **In-memory state.** `level` and `trace` live on the engine instance, so it cannot survive a server restart or a stateless HTTP request. Add `to_state()` / `from_state()` and persist in `SiddhiSession.state`.
9. **`topic_switch` picks `topic_list[0]`** (arbitrary prerequisite) and never returns. The docstring TIP says a student who recovers should climb back to the started topic; `trace` should be used as a stack for this. Better: choose the prerequisite with the lowest mastery for this student.
10. **No evaluator.** Nothing computes the expected answer of a generated expression, and nothing records per-attempt results, so the "final report" cannot be built yet. Need a safe evaluator (small AST walker using `Fraction`; do not call `eval` on strings).
11. Star imports (`from server.service.prashna import *`) hide dependencies; `rcg` is used as an instance but imported as if it were a module. Verify what `server/service/__init__.py` exports.
12. `SiddhiEngine.__init__` stores `self.template` but `generate` re-reads `TEMPLATES[target]`, so the stored template is stale after a topic switch.

### 9.3 `ExpressionEngine` (Chintan)
1. **Demo code runs on import.** The bottom of the file (`let expre = "2*2+2*2"; new ExpressionEngine(...).parse()` plus `console.log`s) executes every time the Vue app imports the module. Delete or move to a test.
2. `operation_order` is assigned but not declared as a class field, which fails under strict TypeScript.
3. `parse()` returns a positional tuple. Return an object `{ dictionary, list, expression }`.
4. It replaces components with `expression.replace(sub_string, tag)`, i.e. string search, not position. It works because operations are always resolved leftmost first, but it is a subtle invariant. A tokenizer plus real parser (AST) removes the fragility and is needed for brackets anyway.
5. No input validation inside the engine. Validation lives only in the Vue file (`validateAndClean`), and a malformed string makes `extract_component` return `undefined`, which crashes on `.join`.
6. Noisy `console.log` in the constructor loop.
7. File is spelled `Arithmatic.ts`. Keep it or rename it, but update the import in the Vue file at the same time.

### 9.4 Chintan Vue file
1. **One file, four jobs**: expression UI, pure block-scene builders (`buildAdd/Sub/Mul/Div`, `scopeProblem`), an imperative canvas renderer, and evaluation logic duplicated from the engine (`STEP_RE`, `evaluateComponent`).
2. The canvas renderer keeps module-level mutable state (`canvas`, `live`, `from`, `goal`, `fades`, ...), so only one canvas can exist at a time. Fine today, fragile later.
3. It has no props or emits, so it cannot be driven by a Siddhi session. It owns its own input box and calls `solve()` at setup.
4. `solve()` runs immediately with the default `2*2+2*2` on mount.

## 10. v1 scope

**In**
- Auth: register, login, `/me`, JWT.
- User + StudentProfile + TopicMastery created at student signup.
- Root graph seeded with the 5 existing topics, loaded, frozen, versioned.
- `StudentGraphView` (frontier, blocked, mastered) and a simple `TopicRanker`.
- Siddhi session over HTTP, restricted to Chintan-compatible flat expressions, with server-side answer checking.
- `apply_report` with idempotency and an event log.
- Front end: login, dashboard listing topics with mastery bars (a list, not a network drawing), session page, Chintan as post-answer explanation.

**Out (later)**
- Brackets and negatives in Chintan; variables in questions.
- BKT / IRT / Elo.
- Admin graph editor UI, root graph version migration tooling.
- Mail service.
- Rollup levels ("1st and 2nd" mastery, see section 12).
- Multiple subjects.

## 11. Build order

| # | Milestone | Done when |
|---|---|---|
| M0 | Cleanup | `ConceptGraph` fixed (9.1), template mutation fixed (9.2.1), engine demo code removed (9.3.1), Vue file split (11.2) |
| M1 | Users end to end | Register, login, `/me` work from the front end |
| M2 | Root graph repo | Graph loads from a file, is frozen, exposes a version hash; `GET /graph/root` works |
| M3 | Student state | `StudentProfile` and `TopicMastery` created on signup; `StudentGraphView.frontier()` and `TopicRanker` unit-tested on a hand-built graph |
| M4 | Siddhi as a service | No global mutation, persisted state, evaluator, batch-score adaptation, Chintan-compatible generation; runs with fake answers in a test |
| M5 | Apply reports | `apply_report` updates `TopicMastery`, writes `MasteryEvent`, is idempotent by `report_id` |
| M6 | Front end loop | Login, dashboard, session page, Chintan explanation after an answer |
| M7 | Hardening | Tests for graph, ranker, report application; error handling; seed data |

### 11.1 Proposed API
`POST /auth/register`, `POST /auth/login`, `GET /me`, `GET /graph/root`, `GET /me/graph`, `GET /me/next-topics`, `POST /sessions`, `POST /sessions/{id}/answers`, `GET /sessions/{id}/report`.

### 11.2 Proposed repository layout

```
server/
  models/            user.py, student.py, mastery.py, session.py
  graph/             concept_graph.py, repository.py, student_view.py (Mool), ranker.py, seed.json
  siddhi/            engine.py, prashna.py, templates.py, evaluator.py, report.py
  services/          graph_sync.py, auth.py
  api/               auth.py, graph.py, sessions.py
  viz/               draw_graph.py           # matplotlib lives here only
chintan/src/
  engine/            expression_engine.ts, evaluate.ts   # replaces Arithmatic.ts
  blocks/            scenes.ts               # pure builders + scopeProblem + types
                     useBlockCanvas.ts       # renderer as a composable/class instance
web/
  ChintanView.vue    # UI; props: expression?, emits: solved / opened
  BlockPlayer.vue    # frame controls + canvas host
```

### 11.3 Later: Chintan grammar
Replace the string-based engine with tokenizer + parser (shunting-yard or recursive descent) producing the same `components_dictionary`, then add brackets and unary minus. "Operation Order" and "Simplification" topics genuinely need brackets, so this is required before those topics are fully usable in Chintan.

## 12. Open questions (UNKNOWN, ask the author)

1. What are the prerequisite edges between the 5 seed topics? (Proposal to confirm: `basic-arithmetic -> variable`, `basic-arithmetic -> operation-order`, `variable -> expression`, `operation-order -> expression`, `expression -> simplification`.)
2. What does "mastery level of total 1st and 2nd" mean? Assumed: rolled-up mastery at hierarchy levels 1 and 2 (for example subject and chapter), derived from leaf topics and not stored. Alternative reading: first-order and second-order mastery.
3. When should Chintan appear: post-answer explanation, practice mode, or both? (See decision 7.)
4. Web framework and DB access layer: FastAPI + SQLModel assumed. Confirm.
5. What do `mool.py` and `prashna_template.py` currently contain?
6. What is the project's actual name, and who is the target learner age group?

## 13. Conventions

- Topic ids are lowercase slugs; display text is an attribute, never a key.
- Root graph edits are admin operations that produce a new version; students are never migrated silently.
- Passwords are hashed with argon2 or bcrypt; hashes never leave the server.
- Siddhi never writes to the database directly; it returns reports.
- Generated questions are stored with their expected answers server-side.
- Use `log` from `server.dev_log`; do not log inside pure lookup functions.
