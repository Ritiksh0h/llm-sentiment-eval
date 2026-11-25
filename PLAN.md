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

- [x] `data/sample_200.jsonl` committed — 200 labelled examples, reproducible
- [x] One script runs a (model, prompt) pair and writes raw results to disk
- [x] One script scores a results file and prints metrics
- [x] All six runs completed, outputs committed
- [x] `README.md` with the 3×2 results table and all six confusion matrices
- [x] Three to five sentences in the README explaining **why** the failures happen,
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

---
---

# v2 — Does the fix work, and does reasoning help?

v1 is complete. It found **no significant difference** at n = 200, and its failure analysis produced
one testable idea: most errors come from TweetEval calling opinions and flatly reported bad news
"neutral", so defining neutral in the prompt should help. v2 tests that idea, and the chain-of-thought
question v1 left out, on enough tweets to actually detect a difference.

**Same rule as v1: the deliverable is the measurement.**

---

## v2 Scope (locked — do not expand)

| Decision | Value |
|---|---|
| Task | Same 3-class sentiment: positive / neutral / negative |
| Dataset | TweetEval sentiment, test split |
| Sample | 800 tweets, **natural class distribution**, fixed seed, **none of v1's 200** |
| Models | DeepSeek `deepseek-flash` and Groq `qwen/qwen3.8-27b`, unchanged from v1 |
| Prompts | v1 zero-shot (`zero_shot.txt`, unchanged) vs neutral-defined zero-shot (`neutral_defined.txt`) |
| Reasoning | Off vs on |
| Temperature | 0 for every run |
| Runs | 8 total (2 models × 2 prompts × 2 reasoning settings), same 800 tweets each |
| Metrics | As v1, plus an exact McNemar test for every paired comparison |

**Why 800:** v1's DeepSeek-vs-Groq gap (5.5 points, with the models disagreeing on 30% of tweets)
needs about 760 tweets to detect at 80% power, p < 0.05. **Why natural distribution:** v1's balanced
sample over-weighted positive. Expect about 259 negative / 387 neutral / 155 positive, all well above
the 40 needed for per-class metrics.

### Out of scope for v2
No Nemotron: it differed from Qwen on only 19 of 200 answers, so it adds cost, not information.
No few-shot: in v1 it moved accuracy by at most 2.5 points. No self-consistency, no RAG, no fine-tuning,
no new task, no UI. **No prompt edits after the first v2 result is seen.**

---

## v2 Definition of done

- [ ] `prompts/neutral_defined.txt` and the three hypotheses committed **before** the first v2 API call
- [ ] `data/sample_800.jsonl` committed: 800 tweets, natural distribution, no overlap with v1 (asserted in code)
- [ ] All eight runs completed, outputs committed in `results/v2/`
- [ ] README v2 section: the 2×2×2 table, paired tests, each hypothesis marked supported or not
- [ ] Failure analysis of the best v2 run, with bucket counts compared against v1's
- [ ] Bucket agreement: a second labeller (or you, blind, a week later), Cohen's kappa reported
- [ ] Variance: the DeepSeek baseline cell run three times, spread reported
- [ ] v1 files still rebuild byte-identical

---

## v2 Phase 1 — Data

1. Extend `src/load_data.py` to also write `data/sample_800.jsonl`: a **plain random** 800 from the
   test split, with v1's 200 ids excluded first. Do not stratify; natural distribution is the point.
2. Assert zero overlap with `data/sample_200.jsonl`.
3. Print the distribution.

**Checkpoint:** roughly 259 / 387 / 155, and `sample_200.jsonl` and `few_shot.txt` have the same md5 as before.

**Trap:** overwriting v1. The v1 sample and prompts must keep rebuilding exactly, or v1's results stop being reproducible.

---

## v2 Phase 2 — Pre-register (before any v2 API call)

1. Write `prompts/neutral_defined.txt`: the v1 zero-shot prompt plus one definition. Draft:

   ```
   Classify the sentiment of the following tweet as positive, neutral, or negative.

   Label the emotion the author expresses, not the topic. An opinion, a demand, or bad news
   stated without emotional language is neutral.

   Respond with exactly one word: positive, neutral, or negative. Do not add punctuation or explanation.

   Tweet: {text}
   ```

2. Write the hypotheses into the README's v2 section:
   - **H1:** on Qwen, the neutral-defined prompt raises neutral recall (v1: 0.42) without lowering
     overall accuracy.
   - **H2:** on DeepSeek, which already over-uses neutral, the same prompt *lowers* positive recall
     further. In other words, the fix is model-specific.
   - **H3:** turning reasoning on changes accuracy less than the prompt does, because most v1 errors
     came from the label convention, not from failures of reasoning.
3. Commit both. The commit timestamp is your proof the hypotheses came first.

**Trap:** peeking. Don't try the new prompt on any of the 800, not even five tweets. To check the
output format, use the **validation** split.

---

## v2 Phase 3 — Harness changes

1. `run_eval.py`: the sample file and reasoning on/off become arguments. Name outputs by every factor,
   e.g. `results/v2/groq_neutraldefined_reason.jsonl`.
2. Reasoning-on settings per provider. Verify each with one call before any full run:
   - DeepSeek: `thinking: {type: enabled}`
   - Groq Qwen: `reasoning_effort: default`. **v1's test showed Qwen on Groq gives no reasoning
     unless asked**, so check the reasoning token count is above zero.
3. Raise `max_tokens` for reasoning runs (e.g. 4000). At v1's 50, reasoning gets cut off and the reply comes back empty.
4. Log `reasoning_tokens` on every row. It proves reasoning actually ran and gives you the cost.
5. Parse only the reply's `content`, never the reasoning text. If reasoning leaks into `content`
   (e.g. `<think>` tags), the unparseable count will show it.

**Checkpoint:** one tweet per (model, reasoning) setting, on the validation split. Four calls, four
clean labels, and reasoning tokens above zero for both reasoning-on calls.

---

## v2 Phase 4 — The eight runs

1. DeepSeek first, all four cells. It has no daily cap.
2. Groq in parallel: 3,200 calls against the free tier's **1,000 requests/day** means about four days.
   The harness is resumable, so run each day until the cap, then rerun.
3. Variance: rerun the DeepSeek zero-shot, reasoning-off cell twice more (1,600 extra DeepSeek calls).

**Trap:** model drift. If `qwen/qwen3.8-27b` or `deepseek-flash` changes or disappears mid-run, stop.
v2 compares against v1's models, so record the change before deciding anything.

---

## v2 Phase 5 — Scoring and hypotheses

1. Score all eight runs with `score.py`.
2. Paired tests for the three factors: prompt (within each model and reasoning setting), reasoning
   (within each model and prompt), and model (within each prompt and reasoning setting).
3. Mark H1–H3 supported or not, using the pre-registered tests only.

**Trap:** multiple comparisons. Twelve paired tests at p < 0.05 have about a 46% chance of at
least one false positive. H1–H3 are the primary results; every other comparison is exploratory, so label it that way.

---

## v2 Phase 6 — Failure analysis

1. Pull the best v2 run's errors and bucket them with v1's six buckets.
2. Compare against v1. Did "takes a side" and "bad news, flat tone" shrink with the new prompt? Did
   sarcasm and missing context shrink with reasoning? Those answers are the story.
3. Have a second person bucket the same errors blind, and report Cohen's kappa
   (`sklearn.metrics.cohen_kappa_score`).
4. Three to five sentences, grounded in tweets you read.

---

## v2 Repo additions

```
data/sample_800.jsonl
prompts/neutral_defined.txt
results/v2/
  {deepseek,groq}_{zeroshot,neutraldefined}_{noreason,reason}.jsonl
  variance/deepseek_zeroshot_noreason_run2.jsonl
  variance/deepseek_zeroshot_noreason_run3.jsonl
```

---

## v2 Order of work

| Step | Phase | Rough effort |
|---|---|---|
| 1 | 800-tweet sample, v1 files unchanged | 1 hour |
| 2 | Pre-register prompt and hypotheses, commit | 1 hour |
| 3 | Harness: reasoning flag, sample arg, settings verified | 2 hours |
| 4 | Eight runs plus variance (mostly waiting on Groq's daily cap) | ~4 days elapsed |
| 5 | Scoring and hypothesis tests | 2 hours |
| 6 | Failure analysis and kappa | 3 hours |
| 7 | README v2 section and limitations | 2 hours |

---

## v3 ideas (not now)

- **Retrieved few-shot:** pick each tweet's nearest labelled train tweets (TF-IDF from scikit-learn,
  no new dependency) instead of three random ones.
- **Contamination check:** label ~200 recent tweets yourself and compare the score against TweetEval's.
- **Nemotron back in**, if v2 shows model family matters.
- **Self-consistency**, only with reasoning on and temperature above 0.
