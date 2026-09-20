import json
from pathlib import Path

MEASUREMENTS_FILE = Path("measurements_gemini.json")

# Gemini 3.6 Flash paid-tier pricing
# Valid through December 31, 2026
INPUT_PRICE_PER_MILLION = 0.75
OUTPUT_PRICE_PER_MILLION = 3.75

REQUESTS_PER_DAY = 2000
DAYS_PER_YEAR = 365

with open(MEASUREMENTS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

model = data["model"]
measurements = data["one_request_billed"]

print("PART 3 — Gemini cost calculation")
print(f"Model: {model}")
print(f"Volume: {REQUESTS_PER_DAY:,} requests/day")
print()

print("ONE SUPPORT REQUEST — cost in USD")
print("-" * 72)
print(
    f"{'Language':<10}"
    f"{'Input':>10}"
    f"{'Output':>12}"
    f"{'Cost/request':>18}"
    f"{'Annual cost':>18}"
)

costs = {}

for lang in ["en", "ru", "kk"]:
    input_tokens = measurements[lang]["input_tokens"]
    output_tokens = measurements[lang]["billable_output_tokens"]

    input_cost = (
        input_tokens / 1_000_000
    ) * INPUT_PRICE_PER_MILLION

    output_cost = (
        output_tokens / 1_000_000
    ) * OUTPUT_PRICE_PER_MILLION

    request_cost = input_cost + output_cost
    annual_cost = request_cost * REQUESTS_PER_DAY * DAYS_PER_YEAR

    costs[lang] = {
        "request_cost": request_cost,
        "annual_cost": annual_cost,
    }

    print(
        f"{lang.upper():<10}"
        f"{input_tokens:>10}"
        f"{output_tokens:>12}"
        f"${request_cost:>16.6f}"
        f"${annual_cost:>17,.2f}"
    )

print()
print("COST RATIOS")
print("-" * 72)

ru_ratio = costs["ru"]["request_cost"] / costs["en"]["request_cost"]
kk_ratio = costs["kk"]["request_cost"] / costs["en"]["request_cost"]

print(f"RU / EN total bill = {ru_ratio:.2f}x")
print(f"KK / EN total bill = {kk_ratio:.2f}x")

print()
print("EXTRA ANNUAL COST VS ENGLISH")
print("-" * 72)

ru_extra = costs["ru"]["annual_cost"] - costs["en"]["annual_cost"]
kk_extra = costs["kk"]["annual_cost"] - costs["en"]["annual_cost"]

print(f"Russian: +${ru_extra:,.2f}/year")
print(f"Kazakh:  +${kk_extra:,.2f}/year")