"""Score a results file: python src/score.py results/deepseek_zeroshot.jsonl"""
import json
import math
import sys

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

LABELS = ["negative", "neutral", "positive"]

rows = [json.loads(l) for l in open(sys.argv[1])]
y_true = [r["true_label"] for r in rows]
y_pred = [r["parsed_label"] for r in rows]
acc = accuracy_score(y_true, y_pred)  # "unparseable" never equals a gold label -> counted wrong
ci = 1.96 * math.sqrt(acc * (1 - acc) / len(rows))

print(f"{sys.argv[1]}: {len(rows)} rows")
print(f"Accuracy: {acc:.3f}  (95% CI ±{ci:.3f})")
print(f"Unparseable: {y_pred.count('unparseable')} (counted as wrong)")
print(f"Non-exact replies (not a bare lowercase label): "
      f"{sum(r['raw_response'].strip() not in LABELS for r in rows)}\n")
print(classification_report(y_true, y_pred, labels=LABELS, digits=3, zero_division=0))

# Unparseable gets its own column so each row sums to the class count.
cols = LABELS + ["unparseable"]
cm = confusion_matrix(y_true, y_pred, labels=cols)[: len(LABELS)]
print("| gold \\ pred | " + " | ".join(cols) + " |")
print("|---" * (len(cols) + 1) + "|")
for label, counts in zip(LABELS, cm):
    print(f"| **{label}** | " + " | ".join(map(str, counts)) + " |")

# Optional paired comparison: python src/score.py A.jsonl B.jsonl (same 200 ids).
# Exact McNemar test: only the tweets where exactly one of the two runs is right carry signal.
if len(sys.argv) > 2:
    other = {r["id"]: r["parsed_label"] for r in map(json.loads, open(sys.argv[2]))}
    only_a = sum(r["parsed_label"] == r["true_label"] != other[r["id"]] for r in rows)
    only_b = sum(other[r["id"]] == r["true_label"] != r["parsed_label"] for r in rows)
    n = only_a + only_b
    p = min(1.0, 2 * sum(math.comb(n, k) for k in range(min(only_a, only_b) + 1)) / 2**n) if n else 1.0
    differ = sum(r["parsed_label"] != other[r["id"]] for r in rows)
    print(f"\nvs {sys.argv[2]}: only this right {only_a}, only other right {only_b}, "
          f"exact McNemar p={p:.3f}; answers differ on {differ}/{len(rows)}")
