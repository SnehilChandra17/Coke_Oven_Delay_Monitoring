import subprocess
import sys
from pathlib import Path


# =========================================================
# PROJECT UPDATE PIPELINE
# =========================================================

print()
print("==============================================")
print(" COKE OVEN DELAY MONITORING SYSTEM")
print(" DATABASE UPDATE PIPELINE")
print("==============================================")
print()


# =========================================================
# 1. CHECK FOR EXCEL FILE
# =========================================================

data_folder = Path("data")

excel_files = list(data_folder.glob("*.xlsm"))

if not excel_files:
    print("ERROR")
    print("----------------------------------------------")
    print("No .xlsm Excel file found inside the data folder.")
    print()
    print("Please place the BSP Excel workbook inside:")
    print("data/")
    print()
    sys.exit(1)


# Select latest modified Excel file
latest_excel = max(
    excel_files,
    key=lambda file: file.stat().st_mtime
)

print("Latest Excel file detected:")
print(f"  {latest_excel}")

print()
print(f"Excel files found: {len(excel_files)}")


# =========================================================
# 2. RUN SCRIPT FUNCTION
# =========================================================

def run_script(script_name):

    print()
    print("----------------------------------------------")
    print(f"Running: {script_name}")
    print("----------------------------------------------")
    print()

    result = subprocess.run(
        [
            sys.executable,
            script_name
        ]
    )

    if result.returncode != 0:

        print()
        print("ERROR")
        print("----------------------------------------------")
        print(f"{script_name} failed.")
        print("Database update stopped.")
        print()

        sys.exit(1)


# =========================================================
# STEP 1 — CLEAN EXCEL DATA
# =========================================================

run_script(
    "scripts/clean_delay_data.py"
)


# =========================================================
# STEP 2 — PREPARE DATABASE DATA
# =========================================================

run_script(
    "scripts/prepare_database_data.py"
)


# =========================================================
# STEP 3 — IMPORT INTO MYSQL
# =========================================================

run_script(
    "scripts/import_database.py"
)


# =========================================================
# COMPLETE
# =========================================================

print()
print("==============================================")
print(" DATABASE UPDATE COMPLETED")
print("==============================================")
print()

print("Latest Excel file processed:")
print(f"  {latest_excel}")

print()
print("Pipeline:")
print("  Excel → Cleaning → Preparation → MySQL")

print()
print("Your database is up to date.")
print()