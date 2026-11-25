# LLM Sentiment Evaluation Harness — Build Plan

An evaluation harness that measures how well LLMs classify sentiment, and whether
prompt design or model choice matters more.

**Not a demo. The deliverable is the measurement, not the classifier.**

---

## Scope (locked — do not expand in v1)

| Decision | Value |
|---|---|
| Task | 3-class sentiment: positive / neutral / negative |
| Dataset | TweetEval sentiment (Hugging Face, human-labelled, free) |
| Sample | 200 examples from the test split, fixed seed |
| Models | Groq, DeepSeek and NVIDIA (Nemotron Ultra), one model each |
| Prompts | Zero-shot and few-shot (3–5 in-prompt examples) |
| Temperature | 0 for every run |
| Runs | 6 total (3 models × 2 prompts), same 200 examples each |
| Metrics | Accuracy, per-class precision/recall/F1, confusion matrix |

### Out of scope for v1
No UI. No deployment. No fine-tuning. No fourth model. No second task.
No chain-of-thought, no self-consistency, no RAG. Those are v2 ideas at best.

---

## Definition of done

Tick all six or it isn't finished:

- [ ] `data/sample_200.jsonl` committed — 200 labelled examples, reproducible
- [ ] One script runs a (model, prompt) pair and writes raw results to disk
- [ ] One script scores a results file and prints metrics
- [ ] All six runs completed, outputs committed
- [ ] `README.md` with the 3×2 results table and all six confusion matrices
- [ ] Three to five sentences in the README explaining **why** the failures happen,
      grounded in actual misclassified examples you read

---

## Phase 1 — Data (do this first, alone)

**Goal:** 200 examples on disk, and you know their class distribution.

1. `pip install datasets` and load TweetEval sentiment, test split.
2. Sample 200 rows with a fixed random seed so the set is reproducible.
3. Save as JSONL with fields: `id`, `text`, `label` (string, not integer).
4. Print the class distribution.

**Checkpoint:** how many positive / neutral / negative did you get?
If one class is under ~40 examples, consider stratified sampling so each class
has enough rows for per-class metrics to mean anything. Write the distribution
into the README — a reader needs it to interpret your accuracy number.

**Trap:** TweetEval labels are integers (0/1/2). Map them to strings once, here,
and never touch the integers again. Mislabelled mapping silently ruins everything
downstream and is hard to spot later.

---

## Phase 2 — One run, end to end

**Goal:** Groq + zero-shot works completely before anything else exists.

1. Write the zero-shot prompt. Demand a single word back: `positive`, `neutral`,
   or `negative`. Nothing else.
2. Call the model per example, temperature 0.
3. Write every result to `results/groq_zeroshot.jsonl` with: `id`, `text`,
   `true_label`, `raw_response`, `parsed_label`.
4. Parse defensively. The model will sometimes return `"Positive."` or
   `"The sentiment is negative"`. Normalise case and strip punctuation. If it
   still doesn't match a valid label, record `parsed_label: "unparseable"` —
   **do not guess and do not drop the row.**

**Checkpoint:** 200 rows in the results file, and a count of unparseable responses.

**Why this matters:** the unparseable count is a finding. "Zero-shot produced N
unparseable outputs; few-shot produced M" is a real result about prompt design
and belongs in the README.

**Trap:** rate limits. Add a short sleep between calls and handle failures so a
timeout at example 147 doesn't lose the first 146. Write results incrementally.

---

## Phase 3 — Scoring

**Goal:** turn a results file into numbers.

1. Overall accuracy.
2. Per-class precision, recall, F1. `sklearn.metrics.classification_report` does
   this in one line.
3. A 3×3 confusion matrix.
4. Count unparseable responses separately and state how you treated them —
   counting them as wrong is the honest default. Say so.

**Checkpoint:** run it on the Groq zero-shot file and read the confusion matrix.
Which class is worst? It is almost certainly neutral. That's your story.

---

## Phase 4 — The other five runs

Only now add variation. The harness already exists; these are parameters.

1. Few-shot prompt: same instruction, plus 3–5 labelled examples.
   **Take them from the train split, never from your 200** — using test examples
   as few-shot examples leaks the answer and invalidates the comparison.
2. Run Groq few-shot. Score it.
3. Swap in DeepSeek. Run both prompts. Score both.
4. Swap in NVIDIA Nemotron Ultra. Run both prompts. Score both.

**Checkpoint:** six results files, six scores, the 3×2 table filled in.

---

## Phase 5 — Failure analysis (the part that makes this worth doing)

**Goal:** explain the numbers. This is the section that separates your project
from every demo.

1. Pull every example the best run got wrong.
2. Read them. Actually read them, twenty at least.
3. Sort the errors into buckets. Likely ones: sarcasm, mixed sentiment in one
   tweet, neutral-vs-mild-positive ambiguity, slang, missing context.
4. Pick two or three examples where **you'd disagree with the gold label**.
   Label noise is real and acknowledging it is a strength, not an excuse.
5. Write three to five sentences. Not "the model struggled with nuance" —
   something a reader could act on.

---

## Phase 6 — README

Structure:

1. **What this is** — one paragraph. An evaluation harness, not a classifier.
2. **Dataset** — TweetEval, 200 test examples, class distribution, fixed seed.
3. **Method** — the 3×2, temperature 0, how responses were parsed, how
   unparseable responses were counted.
4. **Results** — the table, all six confusion matrices.
5. **Failure analysis** — Phase 5.
6. **Limitations** — write these yourself, honestly. At minimum:
   - 200 examples is a small sample; differences of a point or two are noise
   - Possible training contamination: TweetEval predates these models, so part
     of the score may be memorisation rather than capability
   - Single run per cell, so no variance estimate
   - Gold labels contain noise
7. **How to reproduce** — the commands, in order.

The limitations section is the most senior thing in the repo. Most portfolio
projects have none.

---

## Repo layout

```
llm-sentiment-eval/
  data/
    sample_200.jsonl
  prompts/
    zero_shot.txt
    few_shot.txt
  results/
    groq_zeroshot.jsonl
    groq_fewshot.jsonl
    deepseek_zeroshot.jsonl
    deepseek_fewshot.jsonl
    nvidia_zeroshot.jsonl
    nvidia_fewshot.jsonl
  src/
    load_data.py
    run_eval.py
    score.py
  README.md
  requirements.txt
  .env.example      # key names only, never real keys
```

`.gitignore` must contain `.env` before your first commit.

---

## Order of work

| Step | Phase | Rough effort |
|---|---|---|
| 1 | Data loader, 200 examples, distribution printed | 1 hour |
| 2 | Groq zero-shot run end to end | 2–3 hours |
| 3 | Scoring script, first confusion matrix | 1–2 hours |
| 4 | Few-shot prompt + five remaining runs | 2 hours |
| 5 | Failure analysis — read the errors | 2 hours |
| 6 | README | 2 hours |

Realistically a weekend plus an evening. **Phase 1 is the only thing that matters
today.** Do not read ahead and start designing Phase 5.

---

## Things that will go wrong

- **Rate limits.** Free tiers throttle. Sleep between calls, write incrementally,
  make the script resumable.
- **Output drift.** Models return "Positive!" or a sentence. Parse defensively,
  log the raw response always.
- **Few-shot leakage.** Few-shot examples must come from the train split.
- **Silent label mapping bug.** Verify the integer-to-string mapping by eyeballing
  ten examples before you run anything.
- **Scope creep.** The moment you want to add a fourth model or chain-of-thought,
  stop. Finish the six boxes first.

---

## Why this is worth building

Almost every GenAI portfolio project is a demo with no measurement. This one is
measurement with no demo. The skill it shows — define a metric, run a controlled
comparison, read the failures, state the limitations — is the thing teams
actually need and the thing almost nobody practises.

The failure analysis and the limitations section are what make it credible.
Do not skip them to ship faster.
