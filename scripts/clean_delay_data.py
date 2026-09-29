import pandas as pd
from pathlib import Path


# ==========================================
# 1. AUTOMATIC FILE DETECTION
# ==========================================

data_folder = Path("data")

excel_files = list(data_folder.glob("*.xlsm"))

if not excel_files:
    raise FileNotFoundError(
        "No .xlsm Excel file found inside the data folder."
    )

if len(excel_files) > 1:
    print("Multiple Excel files found:")
    for file in excel_files:
        print(" -", file)

    # Select the most recently modified workbook
    file_path = max(
        excel_files,
        key=lambda file: file.stat().st_mtime
    )
else:
    file_path = excel_files[0]

print("Selected Excel file:", file_path)


# ==========================================
# 2. READ DELAY SHEET
# ==========================================

df = pd.read_excel(
    file_path,
    sheet_name="Delay",
    header=4,
    engine="openpyxl"
)

print("Original shape:", df.shape)


# ==========================================
# 3. CLEAN COLUMN NAMES
# ==========================================

df.columns = df.columns.astype(str).str.strip()

print("\nCleaned column names:")

for i, column in enumerate(df.columns):
    print(i, "->", column)


# ==========================================
# 4. KEEP IMPORTANT COLUMNS
# ==========================================

columns_to_keep = [
    "Date",
    "Shift",
    "Delay Type",
    "From HH",
    "From MM",
    "From AMPM",
    "TO HH",
    "TO MM",
    "TO AMPM",
    "Delay",
    "Code Machine",
    "Code Name",
    "Code Mechanism",
    "Code Agency",
    "Code Attended",
    "Machine",
    "Mechanism",
    "Agency",
    "Time",
    "Delay.1",
    "Battery Affected",
    "Attended",
    "Remark.1"
]

missing_columns = [
    column for column in columns_to_keep
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Required columns are missing from the Excel file: "
        f"{missing_columns}"
    )

df = df[columns_to_keep].copy()

# ==========================================
# 4A. CLEAN TEXT VALUES
# ==========================================

text_columns = [
    "Shift",
    "Code Name",
    "Machine",
    "Mechanism",
    "Agency",
    "Battery Affected",
    "Attended",
    "Remark.1"
]

for column in text_columns:
    df[column] = df[column].apply(
        lambda value: value.strip()
        if isinstance(value, str)
        else value
    )


    
# ==========================================
# 5. FORWARD-FILL DATE
# ==========================================

df["Date"] = df["Date"].ffill()


# ==========================================
# 6. REMOVE EMPTY RECORDS
# ==========================================

df = df.dropna(
    subset=[
        "Battery Affected",
        "Machine",
        "Mechanism"
    ],
    how="all"
)


# ==========================================
# 7. CONVERT DATE
# ==========================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)


# ==========================================
# 8. CLEAN DELAY VALUE
# ==========================================

df["Delay"] = pd.to_numeric(
    df["Delay"],
    errors="coerce"
)


# ==========================================
# 9. RENAME COLUMNS
# ==========================================

df = df.rename(
    columns={
        "Delay": "delay_minutes",
        "Delay.1": "delay_text",
        "Battery Affected": "battery",
        "Remark.1": "remark"
    }
)


# ==========================================
# 10. DISPLAY CLEAN DATA
# ==========================================

print("\n====================================")
print("CLEANED DATA")
print("====================================")

print("Shape:", df.shape)

print("\nFirst 10 records:")

print(
    df.head(10).to_string(index=False)
)


# ==========================================
# 11. VALIDATION
# ==========================================

print("\n====================================")
print("VALIDATION")
print("====================================")

print(
    "Number of records:",
    len(df)
)

print(
    "Unique dates:",
    df["Date"].nunique()
)

print(
    "Dates:",
    df["Date"].dropna().dt.strftime("%Y-%m-%d").unique()
)

print(
    "Shifts:",
    df["Shift"].dropna().unique()
)

print(
    "Total delay:",
    df["delay_minutes"].sum(),
    "minutes"
)

print(
    "Unique machines:",
    df["Machine"].nunique()
)

print(
    "Unique mechanisms:",
    df["Mechanism"].nunique()
)

print(
    "Unique agencies:",
    df["Agency"].nunique()
)

print(
    "Unique battery values:",
    df["battery"].nunique()
)


# ==========================================
# 12. SAVE CLEAN DATASET
# ==========================================

output_file = "data/cleaned_delay_records.csv"

df.to_csv(
    output_file,
    index=False
)

print("\n====================================")
print("SUCCESS")
print("====================================")

print(
    "Cleaned dataset saved to:"
)

print(output_file)

