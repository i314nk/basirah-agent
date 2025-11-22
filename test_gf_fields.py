"""
Quick test to see what fields GuruFocus tool actually returns.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.tools.gurufocus_tool import GuruFocusTool
from src.agent.data_structures import AnalysisMetrics

# Initialize tool
tool = GuruFocusTool()

# Fetch summary for AOS
result = tool.execute(ticker="AOS", endpoint="summary")

if result.get("success"):
    data = result.get("data", {})

    print("=" * 80)
    print("GURUFOCUS TOOL OUTPUT STRUCTURE")
    print("=" * 80)
    print()

    # Show raw data structure
    print("DATA KEYS:", list(data.keys()))
    print()

    # Show what fields are in each section
    print(f"METRICS: {type(data.get('metrics'))} - {len(data.get('metrics', {}))} fields")
    if "metrics" in data and data["metrics"]:
        for key in sorted(data["metrics"].keys()):
            print(f"  - {key}: {data['metrics'][key]}")
    else:
        print("  (empty)")
    print()

    print(f"FINANCIALS: {type(data.get('financials'))} - {len(data.get('financials', {}))} fields")
    if "financials" in data and data["financials"]:
        for key in sorted(data["financials"].keys()):
            print(f"  - {key}: {data['financials'][key]}")
    else:
        print("  (empty)")
    print()

    print(f"VALUATION: {type(data.get('valuation'))} - {len(data.get('valuation', {}))} fields")
    if "valuation" in data and data["valuation"]:
        for key in sorted(data["valuation"].keys()):
            print(f"  - {key}: {data['valuation'][key]}")
    else:
        print("  (empty)")
    print()

    print(f"GENERAL: {type(data.get('general'))} - {len(data.get('general', {}))} fields")
    if "general" in data and data["general"]:
        print("  Fields:", list(data["general"].keys())[:10])
    print()

    print(f"RAW_DATA: {type(data.get('raw_data'))}")
    if "raw_data" in data:
        raw = data["raw_data"]
        if isinstance(raw, dict):
            print(f"  Keys: {list(raw.keys())[:15]}")
            if raw.keys():
                for key in raw.keys():
                    print(f"  [{key}]:")
                    if isinstance(raw[key], dict):
                        print(f"    Type: dict, {len(raw[key])} fields")
                        print(f"    Fields: {list(raw[key].keys())}")
                    else:
                        print(f"    Type: {type(raw[key])}, Value: {raw[key]}")
    print()

    print("=" * 80)
    print("ANALYSIS METRICS FIELDS")
    print("=" * 80)
    print()

    # Show what fields AnalysisMetrics has
    metrics = AnalysisMetrics()
    print("AnalysisMetrics fields:")
    for key in sorted(metrics.__dict__.keys()):
        print(f"  - {key}")
    print()

    print("=" * 80)
    print("FIELD MATCHES")
    print("=" * 80)
    print()

    # Check which tool fields match AnalysisMetrics
    tool_fields = set()
    if "metrics" in data:
        tool_fields.update(data["metrics"].keys())
    if "financials" in data:
        tool_fields.update(data["financials"].keys())
    if "valuation" in data:
        tool_fields.update(data["valuation"].keys())

    analysis_fields = set(metrics.__dict__.keys())

    matches = tool_fields.intersection(analysis_fields)
    no_match_tool = tool_fields - analysis_fields
    no_match_analysis = analysis_fields - tool_fields

    print(f"Matching fields ({len(matches)}):")
    for field in sorted(matches):
        print(f"  OK {field}")
    print()

    print(f"Tool fields not in AnalysisMetrics ({len(no_match_tool)}):")
    for field in sorted(no_match_tool):
        print(f"  WARN {field}")
    print()

    print(f"AnalysisMetrics fields not in tool output ({len(no_match_analysis)}):")
    for field in sorted(no_match_analysis):
        print(f"  INFO {field}")
    print()
else:
    print(f"ERROR: {result.get('error')}")
