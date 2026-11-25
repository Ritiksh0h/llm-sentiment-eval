# LLM Sentiment Evaluation Harness

## What this is

An evaluation harness, not a classifier. It measures how well LLMs label tweet sentiment
(positive / neutral / negative) and asks whether **prompt design or model choice** matters more,
using a controlled 3×2 (three models × two prompts) on the same 200 human-labelled tweets.
Every run is scored per class, and the errors were read and explained.
Short answer: on 200 tweets, neither the prompt nor the model moves accuracy by a statistically
detectable amount. What the model changes is *which* tweets get which answer. DeepSeek disagrees with
the other two models on 43–61 tweets, two to three times what a prompt swap changes (18–25). Qwen and
Nemotron behave almost identically, and each model family has its own stable way of getting "neutral" wrong.

## Dataset

TweetEval sentiment (`cardiffnlp/tweet_eval`, config `sentiment`), test split: 12,284 tweets.

200 examples sampled with seed 42, **balanced per class**: 67 negative / 67 neutral / 66 positive.
A plain random 200 gave only 32 positive, too few for per-class metrics to mean anything.
The full test split is 3,972 negative (32%) / 5,937 neutral (48%) / 2,375 positive (19%), so
accuracy here is on a balanced set, not the natural distribution.

`id` in `data/sample_200.jsonl` is the row's index in the original test split. Labels are mapped from
integers to strings once, in `src/load_data.py`, from the dataset's own metadata.

## Method

| | Provider | Model | Reasoning |
|---|---|---|---|
| **DeepSeek** | DeepSeek API | `deepseek-flash` (DeepSeek-V4.1-Flash) | off (`thinking: {type: disabled}`) |
| **Groq** | Groq | `qwen/qwen3.8-27b` | off (`reasoning_effort: none`) |
| **Nemotron** | NVIDIA API | `nvidia/nemotron-3-ultra-550b-a55b` | off (`enable_thinking: false`) |

- **Reasoning off for every model.** All three reason by default; chain-of-thought is out of scope, so
  each run measures direct answers. On Groq this ruled out `gpt-oss-120b` / `20b`, which can't turn reasoning off.
- **Same settings everywhere:** temperature 0, `max_tokens` 50, one user message per tweet, run in November 2026.
- **Prompts.** [`prompts/zero_shot.txt`](prompts/zero_shot.txt) asks for exactly one word.
  [`prompts/few_shot.txt`](prompts/few_shot.txt) is the same instruction word for word plus three
  examples, one per class, drawn at random (seed 42) from the **train** split (train ids 33445, 8027, 2095)
  and checked not to appear anywhere in the test split. They were not hand-picked.
- **Parsing.** Lowercase the reply; if exactly one of the three label words appears, that's the label,
  otherwise `unparseable`. Unparseable replies are **counted as wrong**. The raw reply is always kept.
  In practice all 1,200 replies were a bare lowercase label, so the parser's leniency never mattered.
- **Statistics.** 95% confidence intervals use the normal approximation (about ±6 points at n = 200).
  Runs are compared with an exact McNemar test, since every run sees the same tweets.

## Results

| Accuracy (macro F1) | Zero-shot | Few-shot |
|---|---|---|
| **DeepSeek** | 0.680 (0.683) | 0.700 (0.704) |
| **Groq** | **0.735** (0.716) | 0.710 (0.684) |
| **Nemotron** | 0.715 (0.689) | 0.730 (**0.723**) |

Each accuracy is about ±0.06 (95% CI). Unparseable replies: **0 in every cell**, so on these models
prompt design had no visible effect on output format.

| Run | neg P | neg R | neg F1 | neu P | neu R | neu F1 | pos P | pos R | pos F1 |
|---|---|---|---|---|---|---|---|---|---|
| DeepSeek zero | 0.74 | 0.79 | 0.76 | 0.53 | 0.72 | 0.61 | 0.95 | 0.53 | 0.68 |
| DeepSeek few | 0.78 | 0.79 | 0.79 | 0.55 | 0.73 | 0.63 | 0.88 | 0.58 | 0.70 |
| Groq zero | 0.69 | 0.91 | 0.79 | 0.76 | 0.42 | 0.54 | 0.77 | 0.88 | 0.82 |
| Groq few | 0.65 | 0.93 | 0.76 | 0.72 | 0.34 | 0.46 | 0.79 | 0.86 | 0.83 |
| Nemotron zero | 0.67 | 0.94 | 0.78 | 0.73 | 0.36 | 0.48 | 0.77 | 0.85 | 0.81 |
| Nemotron few | 0.68 | 0.91 | 0.78 | 0.68 | 0.51 | 0.58 | 0.85 | 0.77 | 0.81 |

**Paired comparisons** (same 200 tweets):

| What changes | Comparison | Answers that differ | McNemar p |
|---|---|---|---|
| Prompt | DeepSeek zero → few | 25 | 0.54 |
| Prompt | Groq zero → few | 18 | 0.30 |
| Prompt | Nemotron zero → few | 20 | 0.65 |
| Model, zero-shot | DeepSeek vs Groq | 61 | 0.19 |
| Model, zero-shot | DeepSeek vs Nemotron | 60 | 0.43 |
| Model, zero-shot | Groq vs Nemotron | 19 | 0.48 |
| Model, few-shot | DeepSeek vs Groq | 58 | 0.89 |
| Model, few-shot | DeepSeek vs Nemotron | 43 | 0.43 |
| Model, few-shot | Groq vs Nemotron | 24 | 0.52 |

- **No difference is significant.** The smallest p is 0.19; at n = 200 a gap of a few points is noise.
- **Model family matters more than the prompt for which tweets get which answer.** Swapping the prompt
  changes 18–25 answers. Swapping DeepSeek for either other model changes 43–61. Groq and Nemotron
  differ on only 19–24, about the same as a prompt swap.
- **Each family fails on neutral in its own direction, under both prompts.** DeepSeek uses neutral as a
  fallback (neutral recall 0.72–0.73, but positive recall only 0.53–0.58: positive tweets drift to
  neutral). Qwen and Nemotron avoid neutral (recall 0.34–0.51) and push neutral tweets to negative.
- **Size didn't help.** Nemotron (550B total, 55B active) scored about the same as Qwen 27B. Few-shot
  did lift Nemotron's neutral recall (0.36 → 0.51, +10 tweets), but it lost 5 positives to neutral, so
  accuracy rose only 1.5 points. It is the only model whose per-class pattern the prompt visibly moved.

Confusion matrices (rows = gold, columns = predicted):

**DeepSeek, zero-shot**

| gold \ pred | negative | neutral | positive |
|---|---|---|---|
| **negative** | 53 | 14 | 0 |
| **neutral** | 17 | 48 | 2 |
| **positive** | 2 | 29 | 35 |

**DeepSeek, few-shot**

| gold \ pred | negative | neutral | positive |
|---|---|---|---|
| **negative** | 53 | 14 | 0 |
| **neutral** | 13 | 49 | 5 |
| **positive** | 2 | 26 | 38 |

**Groq, zero-shot**

| gold \ pred | negative | neutral | positive |
|---|---|---|---|
| **negative** | 61 | 3 | 3 |
| **neutral** | 25 | 28 | 14 |
| **positive** | 2 | 6 | 58 |

**Groq, few-shot**

| gold \ pred | negative | neutral | positive |
|---|---|---|---|
| **negative** | 62 | 3 | 2 |
| **neutral** | 31 | 23 | 13 |
| **positive** | 3 | 6 | 57 |

**Nemotron, zero-shot**

| gold \ pred | negative | neutral | positive |
|---|---|---|---|
| **negative** | 63 | 2 | 2 |
| **neutral** | 28 | 24 | 15 |
| **positive** | 3 | 7 | 56 |

**Nemotron, few-shot**

| gold \ pred | negative | neutral | positive |
|---|---|---|---|
| **negative** | 61 | 5 | 1 |
| **neutral** | 25 | 34 | 8 |
| **positive** | 4 | 11 | 51 |

## Failure analysis

Best run by accuracy: Groq `qwen/qwen3.8-27b`, zero-shot, 53 errors out of 200. (Nemotron few-shot has
the best macro F1, 0.723 vs 0.716; that gap is noise.) I read all 53 and put each into one bucket
(every tweet, with all three models' answers: [`results/groq_zeroshot_errors.md`](results/groq_zeroshot_errors.md)).

| Bucket | Errors |
|---|---|
| Takes a side; gold ignores the stance | 16 |
| Factual / promo: unclear neutral vs positive | 10 |
| Bad news in a flat, factual tone | 9 |
| Sarcasm, irony, humour | 8 |
| Missing context, truncated or garbled | 6 |
| Mixed sentiment in one tweet | 4 |

Almost half the errors (24 of 53) are tweets the annotators called neutral that take a side ("Comey Must
be on tRumps payroll", "Stop animal testing #worldwide") or report bad news flatly ("18 Yezidis have fled
ISIS in Tal Afar"): the models label the stance or the topic, while TweetEval's annotators seem to keep
negative and positive for emotion that is actually expressed. The fix that points to is defining neutral
in the instruction ("an opinion, demand or bad news stated without emotional language is neutral"), not
adding examples, which moved accuracy by at most 2.5 points. Another 10 errors sit on a neutral/positive
line the gold labels don't draw consistently ("Random photos from #NBAwards, mostly of poetry judges and
poets" is gold positive; ".@repjohnlewis #NBAwards acceptance speech has been viewed over 1.6 million
times" is gold neutral), so part of the error is a ceiling set by the labels, not the model. The same
kind of tweet (ads, product news, announcements such as "Get $1,000 off a Tesla Model S or X! Use my
promo code") makes up about two-thirds of DeepSeek's 29 positive→neutral misses. Sarcasm, humour and
missing context, the failures people usually expect, are only about a quarter of errors, and some can't
be solved from the text at all: "And Melania trump wrote her own speech" is sarcasm only if you know
about the 2016 plagiarism story.

**Gold labels I disagree with.** All three models gave the same answer, against gold, on each:

- *"Walton family earns more than 130 million Americans - and food stamps and Medicaid funds used to subsidize
  its low wage earners"*: gold **positive**. It's a criticism of the Waltons, so negative.
- *"Yes, including Medicare and social security saving👍"*: gold **neutral**. An explicit yes plus a thumbs-up
  is approval, so positive.
- *"@user @user Comey Must be on tRumps payroll. That would explain a lot!"*: gold **neutral**. An accusation
  with a mocking spelling is negative.

Three models gave the identical wrong answer on 25 of the 53 tweets. Different model families agreeing
against the human label is more likely label noise or genuine ambiguity than a weakness of one model.

## Limitations

- **Small sample.** 200 tweets gives about ±6 points of uncertainty per run, and no difference here is
  significant. Differences of a point or two are noise.
- **Possible training contamination.** TweetEval (2020) is public and predates all three models, so part
  of any score may be memorisation rather than capability.
- **One run per cell, no variance estimate.** Temperature 0 isn't fully deterministic on hosted APIs:
  two identical test calls to DeepSeek returned `positive` and `Positive`.
- **Gold labels contain noise.** See the three disputed labels above, and the inconsistent
  neutral/positive line for factual tweets.
- **Balanced sample, not real-world mix.** Real TweetEval is 48% neutral, the class where the models
  differ most, so accuracy (and possibly the ranking) on the natural distribution would differ.
- **Reasoning was turned off.** These models reason by default; the results say nothing about how
  they'd do with it on.
- **One instruction wording, three random examples.** The few-shot result says nothing about a
  carefully written prompt or well-chosen examples.
- **Hosted models are a snapshot.** Aliases such as `deepseek-flash` can be updated without notice; the
  numbers reflect November 2026.
- **The failure buckets are one person's judgement**, with no second annotator. The neutral-definition
  fix came from reading these test errors, so testing it on the same 200 tweets would be tuning on the
  test set. It needs a fresh sample.

## How to reproduce

```bash
git clone https://github.com/Ritiksh0h/llm-sentiment-eval.git && cd llm-sentiment-eval
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # fill in DEEPSEEK_API_KEY, GROQ_API_KEY and NVIDIA_API_KEY

.venv/bin/python src/load_data.py       # writes data/sample_200.jsonl and prompts/few_shot.txt (deterministic)

.venv/bin/python src/run_eval.py deepseek zero_shot
.venv/bin/python src/run_eval.py deepseek few_shot
.venv/bin/python src/run_eval.py groq zero_shot
.venv/bin/python src/run_eval.py groq few_shot
.venv/bin/python src/run_eval.py nvidia zero_shot
.venv/bin/python src/run_eval.py nvidia few_shot

.venv/bin/python src/score.py results/groq_zeroshot.jsonl                              # one run
.venv/bin/python src/score.py results/deepseek_zeroshot.jsonl results/groq_zeroshot.jsonl  # + paired test
```

`run_eval.py` writes each row as it goes and skips ids already in the results file, so rerun it after a
crash. Delete the results file to start over. The results are committed, so scoring needs no API keys.
