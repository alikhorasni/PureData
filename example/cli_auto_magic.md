# TurboClean Example 02 – CLI auto‑magic (no Python required)
# First create a CSV file:
echo "name,age,salary
Alice,30,50000
Bob,25,60000
,130,70000
Charlie,22," > example_cli.csv

# One command to clean it:
turboclean clean example_cli.csv example_clean.parquet --auto-magic
