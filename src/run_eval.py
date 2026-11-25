"""Run one (model, prompt) pair over data/sample_200.jsonl -> results/<model>_<prompt>.jsonl

Usage: python src/run_eval.py deepseek zero_shot
Resumable: ids already in the results file are skipped, so just rerun after a crash.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = ("positive", "neutral", "negative")

# Both providers speak the OpenAI chat-completions format, so plain urllib covers them.
PROVIDERS = {
    "deepseek": {
        "url": "https://api.deepseek.com/chat/completions",
        "model": "deepseek-flash",  # DeepSeek-V4.1-Flash
        "key": "DEEPSEEK_API_KEY",
        "sleep": 0.2,
        # V4 models reason by default; the plan rules out chain-of-thought, so turn it off.
        "extra": {"thinking": {"type": "disabled"}},
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        # gpt-oss models can't turn reasoning off; Qwen can, which keeps every run a no-CoT comparison.
        "model": "qwen/qwen3.8-27b",
        "key": "GROQ_API_KEY",
        "sleep": 2.0,  # free tier: 8k tokens/min, 1k requests/day
        "extra": {"reasoning_effort": "none"},
    },
    "nvidia": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "key": "NVIDIA_API_KEY",
        "sleep": 2.0,  # free tier ~40 requests/min, no rate-limit headers sent
        "extra": {"chat_template_kwargs": {"enable_thinking": False}},
    },
}


def parse(raw):
    # ponytail: exactly one label word anywhere -> that label. "not positive" would parse as
    # positive; raw_response is always kept so the scorer can audit non-exact replies.
    found = {w for w in re.findall(r"[a-z]+", raw.lower()) if w in LABELS}
    return found.pop() if len(found) == 1 else "unparseable"


assert parse("Positive.") == "positive"
assert parse("The sentiment is negative") == "negative"
assert parse(" neutral\n") == "neutral"
assert parse("positive or negative") == "unparseable"
assert parse("") == "unparseable"


def env(name):
    for line in (ROOT / ".env").read_text().splitlines():
        k, _, v = line.partition("=")
        if k.strip() == name:
            return v.strip().strip("\"'")
    sys.exit(f"{name} missing from .env")


def call(p, key, prompt):
    body = json.dumps({
        "model": p["model"],
        "temperature": 0,
        "max_tokens": 50,
        "messages": [{"role": "user", "content": prompt}],
        **p["extra"],
    }).encode()
    req = urllib.request.Request(p["url"], data=body, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "llm-sentiment-eval",
    })
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)["choices"][0]["message"]["content"] or ""
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:  # auth / bad request: retrying won't help
                raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]!r}") from e
            err = e
        except OSError as e:  # timeouts, resets, DNS
            err = e
        print(f"  retry in {2 ** attempt}s: {err}", file=sys.stderr)
        time.sleep(2 ** attempt)
    raise RuntimeError(f"giving up after 6 attempts: {err}")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in PROVIDERS:
        sys.exit(__doc__ + f"\nProviders: {', '.join(PROVIDERS)}")
    provider, prompt_name = sys.argv[1:]
    p = PROVIDERS[provider]
    key = env(p["key"])
    template = (ROOT / "prompts" / f"{prompt_name}.txt").read_text()
    rows = [json.loads(l) for l in (ROOT / "data" / "sample_200.jsonl").open()]
    out = ROOT / "results" / f"{provider}_{prompt_name.replace('_', '')}.jsonl"
    out.parent.mkdir(exist_ok=True)
    done = {json.loads(l)["id"] for l in out.open()} if out.exists() else set()

    with out.open("a") as f:
        for n, r in enumerate(rows, 1):
            if r["id"] in done:
                continue
            raw = call(p, key, template.replace("{text}", r["text"]))
            row = {"id": r["id"], "text": r["text"], "true_label": r["label"],
                   "raw_response": raw, "parsed_label": parse(raw)}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()  # incremental: a crash at row 147 keeps the first 146
            print(f"{n}/{len(rows)}  {row['parsed_label']:<11} gold={r['label']}")
            time.sleep(p["sleep"])

    results = [json.loads(l) for l in out.open()]
    bad = sum(x["parsed_label"] == "unparseable" for x in results)
    print(f"\n{len(results)} rows in {out.relative_to(ROOT)}, unparseable: {bad}")


if __name__ == "__main__":
    main()
