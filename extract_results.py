import subprocess
import sys

# Run the test and capture output
result = subprocess.run(
    [sys.executable, "test_zts_deep_dive.py"],
    capture_output=True,
    text=True,
    timeout=1800  # 30 minute timeout
)

# Extract just the test results section
lines = result.stdout.split('\n')
in_results = False
for line in lines:
    if '[STEP 3/3]' in line or 'TEST SUMMARY' in line:
        in_results = True
    if in_results:
        print(line)

sys.exit(result.returncode)
