"""Test regex pattern matching for decision extraction."""
import re

# Test string from actual analysis
test_text = """**DECISION: WATCH**
**CONVICTION: MODERATE**
**INTRINSIC VALUE: $195**"""

print("=" * 80)
print("TESTING DECISION REGEX PATTERNS")
print("=" * 80)
print()
print("Test text:")
print(test_text)
print()

# Pattern from buffett_agent.py line 2264
pattern1 = r'\*\*DECISION:\s*(BUY|WATCH|AVOID)\*\*'
match = re.search(pattern1, test_text, re.IGNORECASE)
print(f"Pattern 1: {pattern1}")
print(f"Match: {match}")
if match:
    print(f"Matched text: {match.group(0)}")
    print(f"Captured group: {match.group(1)}")
print()

# Try simpler pattern
pattern2 = r'DECISION:\s*(BUY|WATCH|AVOID)'
match = re.search(pattern2, test_text, re.IGNORECASE)
print(f"Pattern 2: {pattern2}")
print(f"Match: {match}")
if match:
    print(f"Matched text: {match.group(0)}")
    print(f"Captured group: {match.group(1)}")
print()

# Check what the actual text looks like
print("Character codes around 'DECISION:':")
for i, char in enumerate(test_text[:30]):
    print(f"{i}: '{char}' (ord={ord(char)})")
