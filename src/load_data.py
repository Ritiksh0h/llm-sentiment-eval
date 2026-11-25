"""Phase 1: sample 200 TweetEval sentiment test examples -> data/sample_200.jsonl"""
import json
import random
from collections import Counter
from pathlib import Path

from datasets import load_dataset

SEED = 42
N = 200
OUT = Path(__file__).resolve().parent.parent / "data" / "sample_200.jsonl"

test = load_dataset("cardiffnlp/tweet_eval", "sentiment", split="test", token=False)  # public dataset; ignore any stale HF login
# The only int->str mapping in the project, read from the dataset's own metadata, not hardcoded.
names = test.features["label"].names
assert names == ["negative", "neutral", "positive"], names

# Balanced, not natural distribution: a plain random 200 gave only 32 positive (seed 42),
# too few for per-class metrics. Natural test split is ~32% neg / 48% neu / 19% pos.
PER_CLASS = {"negative": 67, "neutral": 67, "positive": 66}
rng = random.Random(SEED)
labels = test["label"]
# id = original test-split index, so any row can be traced back to the source.
idx = sorted(
    i
    for k, name in enumerate(names)
    for i in rng.sample([j for j, l in enumerate(labels) if l == k], PER_CLASS[name])
)
assert len(idx) == N
rows = [{"id": i, "text": test[i]["text"], "label": names[test[i]["label"]]} for i in idx]

OUT.parent.mkdir(exist_ok=True)
OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))

print(f"Wrote {len(rows)} rows to {OUT}")
print("Distribution:", dict(Counter(r["label"] for r in rows)))
print("\nEyeball the mapping:")
for r in rows[:10]:
    print(f"  [{r['label']:>8}] {r['text'][:100]}")

# Few-shot examples: one per class, random, from TRAIN — never test, that would leak answers.
# Not hand-picked: test errors were already seen, so choosing examples would tune on test.
ROOT = OUT.parent.parent
train = load_dataset("cardiffnlp/tweet_eval", "sentiment", split="train", token=False)
shot_rng = random.Random(SEED)
shots = [shot_rng.choice([j for j, l in enumerate(train["label"]) if l == k]) for k in range(len(names))]
shot_rng.shuffle(shots)
test_texts = set(test["text"])
assert not any(train[j]["text"] in test_texts for j in shots), "few-shot example also in test split"

# Same instruction as zero-shot, word for word; only the examples block is added.
instruction, rest = (ROOT / "prompts" / "zero_shot.txt").read_text().split("Tweet: {text}")
examples = "".join(f"Tweet: {train[j]['text']}\nSentiment: {names[train[j]['label']]}\n\n" for j in shots)
(ROOT / "prompts" / "few_shot.txt").write_text(instruction + "Examples:\n\n" + examples + "Tweet: {text}" + rest)
print(f"\nWrote prompts/few_shot.txt with train ids {shots}")
