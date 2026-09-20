import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from texts import CORPUS, LANGUAGES


load_dotenv()

MODEL = "gemini-3.6-flash"
OUTPUT_PATH = Path(__file__).with_name("measurements_gemini.json")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found in .env")

client = genai.Client(api_key=api_key)


def count_text_tokens(text: str) -> int:
    result = client.models.count_tokens(
        model=MODEL,
        contents=text,
    )
    return result.total_tokens


print(f"PART 2 — Gemini measurement")
print(f"Model: {MODEL}\n")

# 1. Count every corpus text
token_counts = {}

print("TOKEN COUNTS")
print("-" * 60)

for item_id, versions in CORPUS.items():
    token_counts[item_id] = {}

    for lang in LANGUAGES:
        tokens = count_text_tokens(versions[lang])
        token_counts[item_id][lang] = tokens

    print(
        f"{item_id:<15} "
        f"EN={token_counts[item_id]['en']:<5} "
        f"RU={token_counts[item_id]['ru']:<5} "
        f"KK={token_counts[item_id]['kk']:<5}"
    )


# 2. Make one real support request in each language
print("\nREAL REQUESTS")
print("-" * 60)

measurements = {}
request_tokens = {}

for lang in LANGUAGES:

    response = client.models.generate_content(
        model=MODEL,
        contents=CORPUS["complaint"][lang],
        config=types.GenerateContentConfig(
            system_instruction=CORPUS["system_prompt"][lang],
            max_output_tokens=2048,
        ),
    )

    usage = response.usage_metadata

    input_tokens = usage.prompt_token_count or 0
    output_tokens = usage.candidates_token_count or 0
    thoughts_tokens = usage.thoughts_token_count or 0

    # Thinking tokens are also part of output-side usage.
    billable_output_tokens = output_tokens + thoughts_tokens

    request_tokens[lang] = input_tokens

    measurements[lang] = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "thoughts_tokens": thoughts_tokens,
        "billable_output_tokens": billable_output_tokens,
    }

    print(f"\n[{lang.upper()}]")
    print(response.text)
    print(
        f"\nInput tokens: {input_tokens}"
        f"\nVisible output tokens: {output_tokens}"
        f"\nThinking tokens: {thoughts_tokens}"
        f"\nBillable output tokens: {billable_output_tokens}"
    )


# 3. Ratios for the actual request
en_tokens = request_tokens["en"]

ru_ratio = request_tokens["ru"] / en_tokens
kk_ratio = request_tokens["kk"] / en_tokens

print("\nMEASURED INPUT-TOKEN RATIOS")
print("-" * 60)
print(f"RU / EN = {ru_ratio:.2f}x")
print(f"KK / EN = {kk_ratio:.2f}x")


# 4. Save everything for the report / Part 3
payload = {
    "provider": "Google Gemini",
    "model": MODEL,
    "token_counts": token_counts,
    "request_tokens": request_tokens,
    "one_request_billed": measurements,
    "ratios": {
        "ru_en": round(ru_ratio, 4),
        "kk_en": round(kk_ratio, 4),
    },
}

OUTPUT_PATH.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"\nSaved results to {OUTPUT_PATH.name}")