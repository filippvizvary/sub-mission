#!/usr/bin/env python3
"""
Nous API client for the sub-mission burn session.
Direct REST, key from env NOUS_BURN_KEY. No config changes.
"""
import os, json, urllib.request

API = "https://inference-api.nousresearch.com/v1/chat/completions"
KEY = os.environ["NOUS_BURN_KEY"]

def chat(model, messages, max_tokens=8192, temperature=0.3):
    req = urllib.request.Request(API,
        data=json.dumps({"model": model, "messages": messages,
                         "max_tokens": max_tokens, "temperature": temperature}).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    u = d.get("usage", {})
    cost = (u.get("prompt_tokens",0)*PRICES[model][0] + u.get("completion_tokens",0)*PRICES[model][1])/1e6
    return d["choices"][0]["message"]["content"], cost, u

PRICES = {  # USD per token
 "anthropic/claude-opus-5.5":   (4e-6, 20e-6),
 "google/gemini-4-argon":       (2e-6, 10e-6),
 "anthropic/claude-sonnet-5.5": (2e-6, 10e-6),
 "google/gemini-3-pro-image":   (2e-6, 12e-6),
}
