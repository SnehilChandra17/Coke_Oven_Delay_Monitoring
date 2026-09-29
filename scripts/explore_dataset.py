import pandas as pd

# Path to the original BSP workbook
file_path = "data/OPRN LOG 8.0 (2).xlsm"

# Load workbook information
excel_file = pd.ExcelFile(
    file_path,
    engine="openpyxl"
)

# Display all sheet names
print("===================================")
print("SHEETS IN BSP WORKBOOK")
print("===================================")

for sheet in excel_file.sheet_names:
    print(sheet)

# Read the Delay sheet without assuming headers
df = pd.read_excel(
    file_path,
    sheet_name="Delay",
    header=None,
    engine="openpyxl"
)

print("\n===================================")
print("DELAY SHEET INFORMATION")
print("===================================")

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\nFirst 15 rows:")
print(df.head(15).to_string())