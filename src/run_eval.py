"""Run one (model, prompt) pair over data/sample_200.jsonl -> results/<model>_<prompt>[_reason].jsonl

Usage: python src/run_eval.py deepseek zero_shot [--reason]
Resumable: ids already in the results file are skipped, so just rerun after a crash.
"""
import argparse
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
        # V4 models reason by default; v1 turned it off. "high" is DeepSeek's own default level.
        "reasoning_off": {"thinking": {"type": "disabled"}},
        "reasoning_on": {"thinking": {"type": "enabled"}, "reasoning_effort": "high"},
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        # gpt-oss models can't turn reasoning off; Qwen can, which keeps every run a no-CoT comparison.
        "model": "qwen/qwen3.8-27b",
        "key": "GROQ_API_KEY",
        "sleep": 2.0,  # free tier: 8k tokens/min, 1k requests/day
        "reasoning_off": {"reasoning_effort": "none"},
        # "default" (or omitting it) gives NO reasoning on this model; low/medium/high do.
        "reasoning_on": {"reasoning_effort": "high"},
    },
    "nvidia": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "key": "NVIDIA_API_KEY",
        "sleep": 2.0,  # free tier ~40 requests/min, no rate-limit headers sent
        "reasoning_off": {"chat_template_kwargs": {"enable_thinking": False}},
        "reasoning_on": {"chat_template_kwargs": {"enable_thinking": True}},  # ~20s per call
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


def call(p, key, prompt, reason=False):
    """Returns (message, usage, finish_reason, latency_ms)."""
    body = json.dumps({
        "model": p["model"],
        "temperature": 0,
        # Reasoning needs room: at 50 the trace gets cut off and the answer never arrives.
        "max_tokens": 4000 if reason else 50,
        "messages": [{"role": "user", "content": prompt}],
        **p["reasoning_on" if reason else "reasoning_off"],
    }).encode()
    req = urllib.request.Request(p["url"], data=body, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "llm-sentiment-eval",
    })
    for attempt in range(6):
        wait = 2 ** attempt
        try:
            t = time.monotonic()
            with urllib.request.urlopen(req, timeout=180 if reason else 60) as r:
                resp = json.load(r)
            choice = resp["choices"][0]
            return (choice["message"], resp.get("usage") or {}, choice.get("finish_reason"),
                    round((time.monotonic() - t) * 1000))
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:  # auth / bad request: retrying won't help
                raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]!r}") from e
            err = e
            wait = float(e.headers.get("retry-after") or wait)  # rate limit says how long
        except OSError as e:  # timeouts, resets, DNS
            err = e
        print(f"  retry in {wait:g}s: {err}", file=sys.stderr)
        time.sleep(wait)
    raise RuntimeError(f"giving up after 6 attempts: {err}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("provider", choices=PROVIDERS)
    ap.add_argument("prompt_name", help="file name in prompts/, without .txt")
    ap.add_argument("--reason", action="store_true", help="turn the model's native reasoning on")
    args = ap.parse_args()
    provider, prompt_name, reason = args.provider, args.prompt_name, args.reason
    p = PROVIDERS[provider]
    key = env(p["key"])
    template = (ROOT / "prompts" / f"{prompt_name}.txt").read_text()
    rows = [json.loads(l) for l in (ROOT / "data" / "sample_200.jsonl").open()]
    out = ROOT / "results" / f"{provider}_{prompt_name.replace('_', '')}{'_reason' if reason else ''}.jsonl"
    out.parent.mkdir(exist_ok=True)
    done = {json.loads(l)["id"] for l in out.open()} if out.exists() else set()

    with out.open("a") as f:
        for n, r in enumerate(rows, 1):
            if r["id"] in done:
                continue
            msg, usage, finish, ms = call(p, key, template.replace("{text}", r["text"]), reason)
            raw = msg.get("content") or ""  # parse the answer only, never the reasoning trace
            row = {"id": r["id"], "text": r["text"], "true_label": r["label"],
                   "raw_response": raw, "parsed_label": parse(raw),
                   "reasoning": msg.get("reasoning_content") or msg.get("reasoning") or "",
                   "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                   "completion_tokens": usage.get("completion_tokens"),
                   "finish_reason": finish, "latency_ms": ms}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()  # incremental: a crash at row 147 keeps the first 146
            print(f"{n}/{len(rows)}  {row['parsed_label']:<11} gold={r['label']}")
            time.sleep(p["sleep"])

    results = [json.loads(l) for l in out.open()]
    bad = sum(x["parsed_label"] == "unparseable" for x in results)
    cut = sum(x.get("finish_reason") == "length" for x in results)
    print(f"\n{len(results)} rows in {out.relative_to(ROOT)}, unparseable: {bad}, truncated: {cut}")
    if reason:  # proof reasoning actually ran (Groq's "default" silently gives none)
        print(f"rows with an empty reasoning trace: {sum(not x.get('reasoning') for x in results)}")


if __name__ == "__main__":
    main()
