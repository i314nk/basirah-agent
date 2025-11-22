"""
Test ROIC extraction after fix
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 60)
print("ROIC EXTRACTION TEST")
print("=" * 60)
print()

# Initialize agent
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)

# Warm cache
print("Warming cache for AOS...")
agent._warm_cache_for_synthesis("AOS", current_year=2024)
print()

# Get metrics from cache
print("=" * 60)
print("EXTRACTING METRICS")
print("=" * 60)
print()

metrics_dict = agent._extract_metrics_from_cache("AOS", 2024)

if metrics_dict:
    roic = metrics_dict.get('roic')
    roe = metrics_dict.get('roe')
    roa = metrics_dict.get('roa')
    operating_margin = metrics_dict.get('operating_margin')
    net_margin = metrics_dict.get('net_margin')

    print(f"ROIC: {roic}")
    print(f"  Type: {type(roic)}")
    if roic is not None:
        print(f"  Value: {roic:.4f} (decimal)")
        print(f"  Percentage: {roic * 100:.2f}%")
    print()

    print(f"ROE: {roe}")
    if roe is not None:
        print(f"  Value: {roe:.4f} (decimal)")
        print(f"  Percentage: {roe * 100:.2f}%")
    print()

    print(f"ROA: {roa}")
    if roa is not None:
        print(f"  Value: {roa:.4f} (decimal)")
        print(f"  Percentage: {roa * 100:.2f}%")
    print()

    print(f"Operating Margin: {operating_margin}")
    if operating_margin is not None:
        print(f"  Value: {operating_margin:.4f} (decimal)")
        print(f"  Percentage: {operating_margin * 100:.2f}%")
    print()

    print(f"Net Margin: {net_margin}")
    if net_margin is not None:
        print(f"  Value: {net_margin:.4f} (decimal)")
        print(f"  Percentage: {net_margin * 100:.2f}%")
    print()

    print("=" * 60)
    print("VALIDATION")
    print("=" * 60)
    print()

    # Expected: ROIC should be around 0.2462 (24.62%)
    if roic is not None:
        if 0.2 <= roic <= 0.35:
            print("[SUCCESS] ROIC is in correct range (20-35%)")
            print(f"  Extracted as: {roic * 100:.2f}%")
        elif roic > 1000:
            print("[FAIL] ROIC shows as DOLLAR AMOUNT (bug not fixed)")
            print(f"  Value: ${roic:.0f}M")
        else:
            print(f"[WARNING] ROIC value unexpected: {roic}")
    else:
        print("[FAIL] ROIC is None (not extracted)")
else:
    print("[FAIL] Failed to extract metrics from cache")

print()
print("=" * 60)
