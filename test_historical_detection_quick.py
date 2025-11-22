"""
Quick test for historical year detection logic
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Test the comparison logic directly
fiscal_periods = [2024, 2023, 2022, 2021, 2020]
year_param_2024 = 2024
year_param_2023 = 2023
year_param_2022 = 2022

most_recent_year = fiscal_periods[0]

print("=" * 60)
print("TESTING HISTORICAL YEAR DETECTION LOGIC")
print("=" * 60)
print()

print(f"fiscal_periods = {fiscal_periods}")
print(f"most_recent_year = fiscal_periods[0] = {most_recent_year}")
print(f"type(most_recent_year) = {type(most_recent_year)}")
print()

# Test year 2024
print(f"Testing year 2024:")
print(f"  year_param = {year_param_2024}")
print(f"  type(year_param) = {type(year_param_2024)}")
print(f"  {year_param_2024} != {most_recent_year} = {year_param_2024 != most_recent_year}")
print(f"  Expected: Should be FALSE (current year)")
print()

# Test year 2023
print(f"Testing year 2023:")
print(f"  year_param = {year_param_2023}")
print(f"  type(year_param) = {type(year_param_2023)}")
print(f"  {year_param_2023} != {most_recent_year} = {year_param_2023 != most_recent_year}")
print(f"  Expected: Should be TRUE (historical year)")
print()

# Test year 2022
print(f"Testing year 2022:")
print(f"  year_param = {year_param_2022}")
print(f"  type(year_param) = {type(year_param_2022)}")
print(f"  {year_param_2022} != {most_recent_year} = {year_param_2022 != most_recent_year}")
print(f"  Expected: Should be TRUE (historical year)")
print()

# Now test with actual agent to see what's being passed
print("=" * 60)
print("TESTING WITH ACTUAL AGENT CODE")
print("=" * 60)
print()

from src.agent.buffett_agent import WarrenBuffettAgent

agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)

# Check most_recent_fiscal_year property
print(f"agent.most_recent_fiscal_year = {agent.most_recent_fiscal_year}")
print(f"type(agent.most_recent_fiscal_year) = {type(agent.most_recent_fiscal_year)}")
print()

# Calculate prior years like the code does
most_recent = agent.most_recent_fiscal_year
year_1 = most_recent - 1 - 0  # First prior year (like i=0)
year_2 = most_recent - 1 - 1  # Second prior year (like i=1)

print(f"Calculated years (like Stage 2 loop):")
print(f"  most_recent = {most_recent} (type: {type(most_recent)})")
print(f"  year_1 = {most_recent} - 1 - 0 = {year_1} (type: {type(year_1)})")
print(f"  year_2 = {most_recent} - 1 - 1 = {year_2} (type: {type(year_2)})")
print()

print("[OK] All types should be 'int' for comparison to work correctly")
print("[OK] Comparisons should return True for historical years (2023, 2022)")
