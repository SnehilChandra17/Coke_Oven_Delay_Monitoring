import pandas as pd
import re

# ==========================================
# LOAD CLEANED DATA
# ==========================================

INPUT_FILE = "data/cleaned_delay_records.csv"

df = pd.read_csv(INPUT_FILE)

print("Original cleaned data shape:", df.shape)


# ==========================================
# CLEAN COLUMN NAMES
# ==========================================

df.columns = df.columns.str.strip()


# ==========================================
# CLEAN BATTERY VALUES
# ==========================================

def split_batteries(value):
    """
    Convert battery values such as:
        11
        9
        3 , 4
    into a list.
    """

    if pd.isna(value):
        return []

    value = str(value).strip()

    # Split using comma
    batteries = value.split(",")

    result = []

    for battery in batteries:
        battery = battery.strip()

        if battery:
            result.append(battery)

    return result


df["battery_list"] = df["battery"].apply(split_batteries)


# ==========================================
# CREATE START TIME
# ==========================================

def create_time(hour, minute, ampm):

    if pd.isna(hour) or pd.isna(minute) or pd.isna(ampm):
        return None

    try:
        hour = int(hour)
        minute = int(minute)

        ampm = str(ampm).strip().upper()

        # Convert 12-hour clock to 24-hour clock
        if ampm == "AM":
            if hour == 12:
                hour = 0

        elif ampm == "PM":
            if hour != 12:
                hour += 12

        return f"{hour:02d}:{minute:02d}:00"

    except Exception:
        return None


df["start_time"] = df.apply(
    lambda row: create_time(
        row["From HH"],
        row["From MM"],
        row["From AMPM"]
    ),
    axis=1
)


# ==========================================
# CREATE END TIME
# ==========================================

df["end_time"] = df.apply(
    lambda row: create_time(
        row["TO HH"],
        row["TO MM"],
        row["TO AMPM"]
    ),
    axis=1
)


# ==========================================
# VALIDATE DELAY
# ==========================================

def calculate_duration(start, end):

    if not start or not end:
        return None

    start_time = pd.to_datetime(start)
    end_time = pd.to_datetime(end)

    # If end time is earlier than start time,
    # assume the delay crossed midnight.
    if end_time < start_time:
        end_time += pd.Timedelta(days=1)

    duration = (end_time - start_time).total_seconds() / 60

    return int(duration)


df["calculated_delay_minutes"] = df.apply(
    lambda row: calculate_duration(
        row["start_time"],
        row["end_time"]
    ),
    axis=1
)


# ==========================================
# COMPARE ORIGINAL VS CALCULATED DELAY
# ==========================================

df["delay_difference"] = (
    df["delay_minutes"]
    - df["calculated_delay_minutes"]
)


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\n====================================")
print("TIME VALIDATION")
print("====================================")

print(
    df[
        [
            "Date",
            "Shift",
            "start_time",
            "end_time",
            "delay_minutes",
            "calculated_delay_minutes",
            "delay_difference"
        ]
    ].head(10).to_string(index=False)
)


# ==========================================
# CHECK FOR MISMATCHES
# ==========================================

mismatches = df[
    df["delay_difference"] != 0
]

print("\n====================================")
print("DELAY VALIDATION")
print("====================================")

print(
    "Records with delay mismatch:",
    len(mismatches)
)

if len(mismatches) > 0:

    print("\nMismatched records:")

    print(
        mismatches[
            [
                "Date",
                "Shift",
                "start_time",
                "end_time",
                "delay_minutes",
                "calculated_delay_minutes",
                "delay_difference"
            ]
        ].to_string(index=False)
    )

else:

    print("All delay durations match successfully.")


# ==========================================
# BATTERY ANALYSIS
# ==========================================

print("\n====================================")
print("BATTERY ANALYSIS")
print("====================================")

print("Battery values:")

for batteries in df["battery_list"]:
    print(batteries)


# ==========================================
# UNIQUE BATTERIES
# ==========================================

unique_batteries = sorted(
    {
        battery
        for battery_list in df["battery_list"]
        for battery in battery_list
    },
    key=lambda x: int(x) if x.isdigit() else x
)

print("\nUnique batteries:")

for battery in unique_batteries:
    print(battery)


# ==========================================
# SAVE PREPARED DATA
# ==========================================

OUTPUT_FILE = "data/prepared_delay_records.csv"

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n====================================")
print("SUCCESS")
print("====================================")

print(
    f"Prepared dataset saved to: {OUTPUT_FILE}"
)