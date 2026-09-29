import ast

import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

import os


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# CONFIGURATION
# =========================================================

CSV_FILE = "data/prepared_delay_records.csv"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv(
    "DB_NAME",
    "coke_oven_monitoring"
)


# =========================================================
# VALIDATE CONFIGURATION
# =========================================================

if not DB_PASSWORD:

    print("ERROR: DB_PASSWORD is missing from .env")

    exit()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_value(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def parse_batteries(value):

    """
    Convert battery_list values such as:

    ['11']

    ['3', '4']

    into:

    [11]

    [3, 4]
    """

    if pd.isna(value):
        return []

    value = str(value).strip()

    if not value:
        return []

    try:

        parsed = ast.literal_eval(value)

        if isinstance(parsed, list):

            return [
                int(str(b).strip())
                for b in parsed
                if str(b).strip()
            ]

    except Exception:
        pass


    # Fallback for unexpected formatting

    value = (
        value
        .replace("[", "")
        .replace("]", "")
        .replace("'", "")
        .replace('"', "")
    )

    batteries = []

    for battery in value.split(","):

        battery = battery.strip()

        if battery:

            batteries.append(
                int(battery)
            )

    return batteries


# =========================================================
# CONNECT TO MYSQL
# =========================================================

print()
print("====================================")
print("MYSQL DATABASE IMPORT")
print("====================================")


try:

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


    if not connection.is_connected():

        print(
            "MySQL connection failed."
        )

        exit()


    print(
        "Connected to MySQL successfully."
    )


except Error as e:

    print(
        "MySQL connection failed."
    )

    print(
        "Error:",
        e
    )

    exit()


cursor = connection.cursor()


# =========================================================
# LOAD CSV
# =========================================================

print()
print("Loading prepared CSV...")


try:

    df = pd.read_csv(
        CSV_FILE
    )

except Exception as e:

    print(
        "Failed to load CSV."
    )

    print(
        "Error:",
        e
    )

    cursor.close()
    connection.close()

    exit()


print(
    "CSV records:",
    len(df)
)


# =========================================================
# IMPORT BATTERIES
# =========================================================

print()
print("Importing batteries...")


all_batteries = set()


for battery_list in df["battery_list"]:

    batteries = parse_batteries(
        battery_list
    )

    for battery in batteries:

        all_batteries.add(
            battery
        )


for battery_number in sorted(
    all_batteries
):

    cursor.execute(
        """
        INSERT IGNORE INTO batteries
        (battery_number)
        VALUES (%s)
        """,
        (
            battery_number,
        )
    )


connection.commit()


print(
    "Batteries processed:",
    len(all_batteries)
)


# =========================================================
# IMPORT MACHINES
# =========================================================

print()
print("Importing machines...")


for _, row in df.iterrows():

    machine_name = clean_value(
        row["Machine"]
    )

    machine_code = row[
        "Code Machine"
    ]


    if machine_name is None:
        continue


    if pd.notna(machine_code):

        machine_code = int(
            machine_code
        )

    else:

        machine_code = None


    cursor.execute(
        """
        INSERT IGNORE INTO machines
        (
            machine_code,
            machine_name
        )
        VALUES (%s, %s)
        """,
        (
            machine_code,
            machine_name
        )
    )


connection.commit()


# Retrieve machine IDs

machines = {}


cursor.execute(
    """
    SELECT
        id,
        machine_name
    FROM machines
    """
)


for machine_id, machine_name in cursor.fetchall():

    machines[
        machine_name
    ] = machine_id


print(
    "Machines available:",
    len(machines)
)


# =========================================================
# IMPORT MECHANISMS
# =========================================================

print()
print("Importing mechanisms...")


for _, row in df.iterrows():

    mechanism_name = clean_value(
        row["Mechanism"]
    )

    mechanism_code = row[
        "Code Mechanism"
    ]


    if mechanism_name is None:
        continue


    if pd.notna(mechanism_code):

        mechanism_code = int(
            mechanism_code
        )

    else:

        mechanism_code = None


    cursor.execute(
        """
        INSERT IGNORE INTO mechanisms
        (
            mechanism_code,
            mechanism_name
        )
        VALUES (%s, %s)
        """,
        (
            mechanism_code,
            mechanism_name
        )
    )


connection.commit()


# Retrieve mechanism IDs

mechanisms = {}


cursor.execute(
    """
    SELECT
        id,
        mechanism_name
    FROM mechanisms
    """
)


for mechanism_id, mechanism_name in cursor.fetchall():

    mechanisms[
        mechanism_name
    ] = mechanism_id


print(
    "Mechanisms available:",
    len(mechanisms)
)


# =========================================================
# IMPORT AGENCIES
# =========================================================

print()
print("Importing agencies...")


for _, row in df.iterrows():

    agency_name = clean_value(
        row["Agency"]
    )

    agency_code = row[
        "Code Agency"
    ]


    if agency_name is None:
        continue


    if pd.notna(agency_code):

        agency_code = int(
            agency_code
        )

    else:

        agency_code = None


    cursor.execute(
        """
        INSERT IGNORE INTO agencies
        (
            agency_code,
            agency_name
        )
        VALUES (%s, %s)
        """,
        (
            agency_code,
            agency_name
        )
    )


connection.commit()


# Retrieve agency IDs

agencies = {}


cursor.execute(
    """
    SELECT
        id,
        agency_name
    FROM agencies
    """
)


for agency_id, agency_name in cursor.fetchall():

    agencies[
        agency_name
    ] = agency_id


print(
    "Agencies available:",
    len(agencies)
)


# =========================================================
# IMPORT DELAY RECORDS
# =========================================================

print()
print("Processing delay records...")


new_records = 0
skipped_records = 0
battery_links_added = 0


for _, row in df.iterrows():

    # -----------------------------------------------------
    # BASIC VALUES
    # -----------------------------------------------------

    delay_date = pd.to_datetime(
        row["Date"]
    ).date()


    shift = clean_value(
        row["Shift"]
    )


    delay_type = (

        int(row["Delay Type"])

        if pd.notna(
            row["Delay Type"]
        )

        else None

    )


    start_time = clean_value(
        row["start_time"]
    )


    end_time = clean_value(
        row["end_time"]
    )


    delay_minutes = int(
        row["delay_minutes"]
    )


    delay_text = clean_value(
        row["delay_text"]
    )


    machine_name = clean_value(
        row["Machine"]
    )


    mechanism_name = clean_value(
        row["Mechanism"]
    )


    agency_name = clean_value(
        row["Agency"]
    )


    attended = clean_value(
        row["Attended"]
    )


    remark = clean_value(
        row["remark"]
    )


    # -----------------------------------------------------
    # FOREIGN KEY IDs
    # -----------------------------------------------------

    machine_id = machines.get(
        machine_name
    )


    mechanism_id = mechanisms.get(
        mechanism_name
    )


    agency_id = agencies.get(
        agency_name
    )


    # -----------------------------------------------------
    # BATTERIES FOR THIS RECORD
    # -----------------------------------------------------

    battery_numbers = parse_batteries(
        row["battery_list"]
    )


    # -----------------------------------------------------
    # CHECK WHETHER RECORD ALREADY EXISTS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT id

        FROM delay_records

        WHERE
            delay_date = %s

            AND shift = %s

            AND delay_type <=> %s

            AND start_time <=> %s

            AND end_time <=> %s

            AND delay_minutes = %s

            AND delay_text <=> %s

            AND machine_id <=> %s

            AND mechanism_id <=> %s

            AND agency_id <=> %s

            AND attended <=> %s

            AND remark <=> %s

        LIMIT 1
        """,
        (
            delay_date,
            shift,
            delay_type,
            start_time,
            end_time,
            delay_minutes,
            delay_text,
            machine_id,
            mechanism_id,
            agency_id,
            attended,
            remark
        )
    )


    existing_record = cursor.fetchone()


    # =====================================================
    # EXISTING RECORD
    # =====================================================

    if existing_record:

        delay_id = existing_record[0]

        skipped_records += 1


    # =====================================================
    # NEW RECORD
    # =====================================================

    else:

        cursor.execute(
            """
            INSERT INTO delay_records
            (
                delay_date,
                shift,
                delay_type,
                start_time,
                end_time,
                delay_minutes,
                delay_text,
                machine_id,
                mechanism_id,
                agency_id,
                attended,
                remark
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                delay_date,
                shift,
                delay_type,
                start_time,
                end_time,
                delay_minutes,
                delay_text,
                machine_id,
                mechanism_id,
                agency_id,
                attended,
                remark
            )
        )


        delay_id = cursor.lastrowid

        new_records += 1


    # =====================================================
    # BATTERY RELATIONSHIPS
    # =====================================================

    for battery_number in battery_numbers:

        cursor.execute(
            """
            SELECT id

            FROM batteries

            WHERE battery_number = %s
            """,
            (
                battery_number,
            )
        )


        battery_result = cursor.fetchone()


        if not battery_result:

            continue


        battery_id = battery_result[0]


        # -------------------------------------------------
        # CHECK RELATIONSHIP
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT 1

            FROM delay_batteries

            WHERE
                delay_id = %s

                AND battery_id = %s

            LIMIT 1
            """,
            (
                delay_id,
                battery_id
            )
        )


        relationship_exists = (
            cursor.fetchone()
            is not None
        )


        # -------------------------------------------------
        # ADD RELATIONSHIP
        # -------------------------------------------------

        if not relationship_exists:

            cursor.execute(
                """
                INSERT INTO delay_batteries
                (
                    delay_id,
                    battery_id
                )

                VALUES
                (
                    %s,
                    %s
                )
                """,
                (
                    delay_id,
                    battery_id
                )
            )


            battery_links_added += 1


# =========================================================
# COMMIT EVERYTHING
# =========================================================

connection.commit()


# =========================================================
# IMPORT SUMMARY
# =========================================================

print()
print("====================================")
print("IMPORT COMPLETE")
print("====================================")


print(
    "CSV records:",
    len(df)
)


print(
    "New records inserted:",
    new_records
)


print(
    "Existing records skipped:",
    skipped_records
)


print(
    "Battery relationships added:",
    battery_links_added
)


# =========================================================
# DATABASE COUNTS
# =========================================================

tables = [
    "batteries",
    "machines",
    "mechanisms",
    "agencies",
    "delay_records",
    "delay_batteries"
]


print()
print("DATABASE COUNTS")
print("------------------------------------")


for table in tables:

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM {table}
        """
    )


    count = cursor.fetchone()[0]


    print(
        f"{table:<20} {count}"
    )


# =========================================================
# VERIFY TOTAL DELAY
# =========================================================

cursor.execute(
    """
    SELECT
        COALESCE(
            SUM(delay_minutes),
            0
        )

    FROM delay_records
    """
)


total_delay = cursor.fetchone()[0]


print()
print(
    "Total delay minutes:",
    total_delay
)


# =========================================================
# CLOSE CONNECTION
# =========================================================

cursor.close()

connection.close()


print()
print("MySQL connection closed.")

print()
print("SUCCESS!")