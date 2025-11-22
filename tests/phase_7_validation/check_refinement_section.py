"""Check for refinement section and thinking tokens in NVO analysis."""
import json

# Load the analysis
with open(r'c:\Projects\basira-agent\basirah_analyses\deep_dive\avoid\NVO_2025-11-15_avoid_131550_5y.json') as f:
    data = json.load(f)

thesis = data['thesis']

# Check for refinement section
print("=" * 80)
print("CHECKING FOR REFINEMENT SECTION")
print("=" * 80)
print()

idx = thesis.find('Current Leadership (ADDED)')
if idx != -1:
    print(f"Found 'Current Leadership (ADDED)' at index {idx}")
    print()
    print("Section content:")
    print("-" * 80)
    print(thesis[idx:idx+3000])
    print("-" * 80)
else:
    print("Not found: 'Current Leadership (ADDED)'")

# Check for thinking tokens
print()
print("=" * 80)
print("CHECKING FOR THINKING TOKENS")
print("=" * 80)
print()

thinking_markers = ['<thinking>', '<think>', '```thinking', 'Let me think']
for marker in thinking_markers:
    count = thesis.count(marker)
    if count > 0:
        print(f"Found {count} instances of '{marker}'")
        idx = thesis.find(marker)
        print(f"  First occurrence at index {idx}")
        print(f"  Context: ...{thesis[max(0, idx-50):idx+100]}...")
        print()

# Check decision extraction
print()
print("=" * 80)
print("DECISION EXTRACTION")
print("=" * 80)
print()

print(f"JSON decision: {data.get('decision')}")
print(f"JSON conviction: {data.get('conviction')}")
print()

# Look for decision in thesis
decision_idx = thesis.rfind('**DECISION:')
if decision_idx != -1:
    print(f"Found '**DECISION:' at index {decision_idx}")
    print("Context:")
    print(thesis[decision_idx:decision_idx+500])
else:
    print("'**DECISION:' not found in thesis")
