"""
Test deep dive analysis on Coca-Cola (KO) with context management.
"""
import os
from dotenv import load_dotenv
from src.agent.buffett_agent import WarrenBuffettAgent
import json

# Load API keys
load_dotenv()

print("="*80)
print("TESTING DEEP DIVE ANALYSIS: COCA-COLA (KO)")
print("="*80)
print()
print("Ticker: KO (The Coca-Cola Company)")
print("Analysis Type: Deep Dive (multi-year with progressive summarization)")
print()
print("Expected cost: ~$2-5")
print("Expected time: 3-5 minutes")
print()

input("Press ENTER to start the analysis (or Ctrl+C to cancel)...")

print("\nInitializing Warren Buffett AI Agent...")
agent = WarrenBuffettAgent()

print("\nStarting deep dive analysis on KO...")
print("="*80)
print()

try:
    result = agent.analyze_company("KO", deep_dive=True)

    print("\n" + "="*80)
    print("DEEP DIVE ANALYSIS COMPLETE - COCA-COLA")
    print("="*80)
    print()

    print(f"Ticker: {result['ticker']}")
    print(f"Decision: {result['decision']}")
    print(f"Conviction: {result['conviction']}")
    print()

    if result.get('intrinsic_value'):
        print(f"Intrinsic Value: ${result['intrinsic_value']:.2f}")
    if result.get('current_price'):
        print(f"Current Price: ${result['current_price']:.2f}")
    if result.get('margin_of_safety'):
        print(f"Margin of Safety: {result['margin_of_safety']*100:.1f}%")
    print()

    # Context management info
    if 'context_management' in result.get('metadata', {}):
        cm = result['metadata']['context_management']
        print("Context Management:")
        print(f"  Strategy: {cm.get('strategy', 'N/A')}")
        print(f"  Years Analyzed: {cm.get('years_analyzed', [])}")
        print(f"  Current Year Tokens: ~{cm.get('current_year_tokens', 0):,}")
        print(f"  Prior Years Tokens: ~{cm.get('prior_years_tokens', 0):,}")
        print(f"  Total Estimated Tokens: ~{cm.get('total_token_estimate', 0):,}")
        print()

        if cm.get('total_token_estimate', 0) < 200000:
            print(f"  STATUS: PASS - Context within 200K limit")
        else:
            print(f"  STATUS: FAIL - Context exceeds 200K limit!")
        print()

    print(f"Tool Calls: {result['metadata'].get('tool_calls_made', 0)}")
    print(f"Duration: {result['metadata'].get('analysis_duration_seconds', 0):.1f} seconds")
    print()

    print("-"*80)
    print("INVESTMENT THESIS (First 1000 chars):")
    print("-"*80)
    # Handle unicode for Windows console
    thesis_preview = result['thesis'][:1000].encode('ascii', errors='replace').decode('ascii')
    print(thesis_preview)
    print("...\n")

    # Save full result to file
    with open('test_deep_dive_ko_result.json', 'w') as f:
        result_json = {
            'ticker': result['ticker'],
            'decision': result['decision'],
            'conviction': result['conviction'],
            'intrinsic_value': result.get('intrinsic_value'),
            'current_price': result.get('current_price'),
            'margin_of_safety': result.get('margin_of_safety'),
            'metadata': result.get('metadata', {}),
            'analysis_summary': result.get('analysis_summary', {}),
            'thesis_length': len(result['thesis'])
        }
        json.dump(result_json, f, indent=2, default=str)

    print("\nFull result saved to: test_deep_dive_ko_result.json")
    print("\nCOCA-COLA TEST COMPLETE!")

except Exception as e:
    print(f"\nERROR: Analysis failed")
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
