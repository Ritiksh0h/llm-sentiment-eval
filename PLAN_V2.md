# V2, Part 1 — Chain-of-Thought and Self-Consistency

Two experiments that close two limitations you already wrote in the V1 README.
Both reuse the existing harness. Neither needs Azure, Power BI, or new infrastructure.

**Do these before the drift monitor.** They strengthen the repo you already have,
and the monitor inherits a more thorough baseline.

---

## Experiment A — Chain-of-thought

### The limitation this closes

> "**Reasoning was turned off.** These models reason by default; the results say
> nothing about how they'd do with it on."

### Design

Same 200 tweets, same two prompts, same two models — reasoning **on**.

| | Zero-shot + CoT | Few-shot + CoT |
|---|---|---|
| DeepSeek | Run 7 | Run 8 |
| Groq | Run 9 | Run 10 |

Nemotron optional, same as V1.

### Decisions to make before coding

**1. Native reasoning, or prompted reasoning?** These are different things and the
distinction matters in the README.

- *Native*: flip the flags you already disabled — `thinking: {type: enabled}` on
  DeepSeek, `reasoning_effort` on Groq. The model reasons internally; you may not
  see the trace.
- *Prompted*: keep reasoning off, append "Think step by step, then give your
  answer on the last line as a single word." You see the reasoning and can read it.

**Recommendation: do prompted first.** You can read the reasoning, which feeds
the failure analysis, and the parsing change is small. Native is a second
comparison if you want it.

**Decided (2026-11-25): native.** All three APIs return the reasoning trace in a separate
field, so native reasoning is readable too. It needs no prompt change and no last-line parser,
and it's the same switch v2 Part 2 uses. Settings: DeepSeek `thinking: enabled` +
`reasoning_effort: high` (its default level); Groq `reasoning_effort: high`. On Groq's Qwen,
`default` or leaving it out gives **no** reasoning, which was verified. Run with `--reason`; outputs go to
`results/<model>_<prompt>_reason.jsonl`, next to the v1 files for the same 200 tweets.

**2. Parsing changes.** Your V1 parser assumes a bare label. CoT replies will be
paragraphs. Take the **last line** and apply the existing parser to it. Keep the
full reply in `raw_response` — you will want to read the reasoning later.

This is the one real code change. Everything else is configuration.

**3. `max_tokens`.** V1 used 50. CoT needs more — 300 to 500. Too low and replies
truncate mid-reasoning and parse as unparseable, which would look like a model
failure when it's a config bug.

### What to measure

Everything V1 measured, plus:

- **Unparseable count.** V1 had 0 in every cell. CoT will likely break that, and
  the number is a finding about output reliability, not just a nuisance.
- **Latency and token count per call.** CoT costs more. If accuracy is flat and
  cost is 6× higher, that's the headline.
- **McNemar, CoT vs non-CoT**, same model and prompt. Paired, same 200 tweets.

### Likely outcome, so you aren't surprised

On 3-class sentiment, CoT often does **not** help, and sometimes hurts — the model
talks itself out of a correct first instinct. If that's what you find, it's a
better result than an improvement, because it's counterintuitive and you can show
it with the reasoning traces.

### Read the traces

Pull 20 cases where CoT and non-CoT disagree. Ten where CoT fixed an error, ten
where CoT broke a correct answer. The second group is the interesting one.

---

## Experiment B — Self-consistency and variance

### The limitations this closes

> "**One run per cell, no variance estimate.** Temperature 0 isn't fully
> deterministic on hosted APIs: two identical test calls to DeepSeek returned
> `positive` and `Positive`."

### This is two experiments in one. Keep them separate.

**B1 — Variance at temperature 0.**
Run one cell (suggest: Groq zero-shot, your best V1 run) **five times, unchanged**,
temperature 0. Measure:
- Accuracy per run, and the spread
- How many of the 200 tweets got a different answer across the five runs
- Whether differences are real label changes or just formatting (`positive` vs `Positive`)

This tells you how much of V1's 0.680-to-0.735 range was noise. If spread is ±3
points, every V1 comparison needs re-reading, and you should say so.

**B2 — Self-consistency voting.**
Same cell, five runs at **temperature 0.7**, majority vote across the five.
Compare the voted result against the single temperature-0 run.

Report: voted accuracy, single-run accuracy, and how often the five runs were
unanimous. Unanimity rate is a cheap confidence signal — tweets where the model
flip-flops are the ambiguous ones, and they should overlap with your V1 failure
buckets.

### Decisions

**1. Which cell?** One. Five runs each on all four cells is 4,000 calls for little
extra insight. Groq zero-shot is the right pick — best V1 accuracy, so improvement
is a real result rather than regression to the mean.

**2. Tie-breaking.** With five votes across three classes, ties are possible
(2-2-1). Decide the rule **before** you run: suggest falling back to the
temperature-0 answer, and report how often ties happened.

**3. Cost.** 5 × 200 × 2 (B1 and B2) = 2,000 calls. Still free tier, but add the
sleep and resume logic you already have.

### The interesting cross-check

Tweets where the five runs **disagree** should correlate with your V1 failure
buckets — sarcasm, mixed sentiment, the neutral/positive boundary. If they do,
you've found a way to flag ambiguous inputs without human labels. That's a
genuinely useful finding and worth its own paragraph.

---

## Code changes needed

| File | Change |
|---|---|
| `src/run_eval.py` | `--cot` flag (appends CoT instruction, raises `max_tokens`); `--temperature`; `--runs N` with run index in the output filename |
| `src/run_eval.py` | Parser: if CoT, parse the **last line**; always keep full `raw_response` |
| `src/run_eval.py` | Log `latency_ms` and token counts per call |
| `src/score.py` | Majority-vote scoring across N result files; unanimity rate; tie count |
| `src/score.py` | Variance report: accuracy spread and answer-change count across runs |
| `prompts/` | `zero_shot_cot.txt`, `few_shot_cot.txt` |

Everything else stays. The harness was built for this.

---

## Order of work

| Step | Effort |
|---|---|
| 1. CoT prompts + last-line parser + `max_tokens` bump | 1 hour |
| 2. Four CoT runs | 1 hour (mostly waiting) |
| 3. Score, McNemar vs V1 runs | 1 hour |
| 4. Read 20 disagreements, write findings | 1 hour |
| 5. B1: five runs at temp 0, variance report | 1–2 hours |
| 6. B2: five runs at temp 0.7, voting + tie rule | 1–2 hours |
| 7. README update: new tables, revised limitations | 2 hours |

One long day, or two evenings.

---

## README changes when done

- **Method**: add a reasoning row to the model table; say prompted vs native
- **Results**: extend the accuracy table with CoT columns; add a cost/latency column
- **New section — Variance**: the B1 spread, and a sentence re-reading V1's
  comparisons in light of it
- **New section — Self-consistency**: voted vs single, unanimity rate, overlap
  between disagreement and the V1 failure buckets
- **Limitations**: delete the two you've now closed. Add new ones — one cell only
  for variance, single tie-break rule, prompted CoT not native.

Deleting limitations you've closed is the point. It shows the README is a live
document, not a one-time write-up.

---

## Scope discipline

Not in this round: fine-tuning, RAG, a third prompt style, more models, Azure,
Power BI. Those come after, and the drift monitor is the next build.

Done means: CoT runs scored, variance measured, voting measured, README updated,
two limitations deleted. Six things.
