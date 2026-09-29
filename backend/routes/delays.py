from datetime import date as DateType
from datetime import time as TimeType

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import get_db


router = APIRouter(
    prefix="/api/delays",
    tags=["Delays"]
)


# =========================================================
# SEARCH DELAY RECORDS
# =========================================================

@router.get("/")
def get_delays(
    battery: int = Query(
        ...,
        gt=0,
        description="Battery number, e.g. 3, 4, 5, 7, 8, 9, 11"
    ),

    date: DateType = Query(
        ...,
        description="Delay date in YYYY-MM-DD format"
    ),

    time: TimeType | None = Query(
        None,
        description="Optional search time in HH:MM format"
    ),

    db: Session = Depends(get_db)
):

    try:

        # =================================================
        # 1. CHECK BATTERY
        # =================================================

        battery_query = text("""
            SELECT
                id,
                battery_number
            FROM batteries
            WHERE battery_number = :battery
            LIMIT 1
        """)

        battery_result = db.execute(
            battery_query,
            {
                "battery": battery
            }
        ).mappings().first()


        if battery_result is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Battery {battery} was not found. "
                    f"Available batteries are 3, 4, 5, 7, 8, 9 and 11."
                )
            )


        battery_id = battery_result["id"]


        # =================================================
        # 2. GET DELAY RECORDS
        # =================================================

        query = text("""
            SELECT
                dr.id AS id,
                dr.delay_date AS delay_date,
                dr.shift AS shift,

                b.battery_number AS battery_number,

                m.machine_name AS machine_name,

                me.mechanism_name AS mechanism_name,

                a.agency_name AS agency_name,

                dr.start_time AS start_time,
                dr.end_time AS end_time,

                dr.delay_minutes AS delay_minutes,

                dr.attended AS attended,
                dr.remark AS remark

            FROM delay_records dr

            INNER JOIN delay_batteries db
                ON dr.id = db.delay_id

            INNER JOIN batteries b
                ON db.battery_id = b.id

            LEFT JOIN machines m
                ON dr.machine_id = m.id

            LEFT JOIN mechanisms me
                ON dr.mechanism_id = me.id

            LEFT JOIN agencies a
                ON dr.agency_id = a.id

            WHERE
                db.battery_id = :battery_id
                AND dr.delay_date = :delay_date

            ORDER BY
                dr.start_time
        """)


        result = db.execute(
            query,
            {
                "battery_id": battery_id,
                "delay_date": date
            }
        ).mappings().all()


        # =================================================
        # 3. PROCESS RECORDS
        # =================================================

        records = []


        for row in result:

            start_time = row["start_time"]
            end_time = row["end_time"]


            # ---------------------------------------------
            # OPTIONAL TIME FILTER
            # ---------------------------------------------

            if time is not None:

                search_time = time


                if start_time is not None and end_time is not None:

                    # Normal range
                    #
                    # Example:
                    # 06:00 -> 14:00
                    #
                    if start_time <= end_time:

                        if not (
                            start_time
                            <= search_time
                            <= end_time
                        ):
                            continue


                    # Overnight range
                    #
                    # Example:
                    # 22:00 -> 06:00
                    #
                    else:

                        if not (
                            search_time >= start_time
                            or search_time <= end_time
                        ):
                            continue


            # ---------------------------------------------
            # SAFE VALUES
            # ---------------------------------------------

            delay_minutes = row["delay_minutes"] or 0


            records.append({

                "id":
                    row["id"],

                "date":
                    str(row["delay_date"]),

                "shift":
                    row["shift"],

                "battery":
                    row["battery_number"],

                "machine":
                    row["machine_name"],

                "mechanism":
                    row["mechanism_name"],

                "agency":
                    row["agency_name"],

                "start_time":
                    str(start_time)
                    if start_time is not None
                    else None,

                "end_time":
                    str(end_time)
                    if end_time is not None
                    else None,

                "delay_minutes":
                    delay_minutes,

                "delay_hours":
                    round(
                        delay_minutes / 60,
                        2
                    ),

                "attended":
                    row["attended"],

                "remark":
                    row["remark"]
            })


        # =================================================
        # 4. TOTALS
        # =================================================

        total_delay = sum(
            record["delay_minutes"]
            for record in records
        )


        total_delay_hours = round(
            total_delay / 60,
            2
        )


        # =================================================
        # 5. RESPONSE
        # =================================================

        return {

            "battery":
                battery,

            "date":
                str(date),

            "time":
                str(time)
                if time is not None
                else None,

            "total_records":
                len(records),

            "total_delay_minutes":
                total_delay,

            "total_delay_hours":
                total_delay_hours,

            "records":
                records
        }


    except HTTPException:

        # Keep our intentional 404 errors
        raise


    except Exception as e:

        # Print actual error in terminal
        print("\n========================================")
        print("ERROR IN /api/delays/")
        print("========================================")
        print(type(e).__name__)
        print(str(e))
        print("========================================\n")


        raise HTTPException(
            status_code=500,
            detail=f"Database/API error: {str(e)}"
        )