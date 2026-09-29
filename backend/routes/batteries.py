from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import get_db


router = APIRouter(
    prefix="/api/batteries",
    tags=["Batteries"]
)


# =========================================================
# GET ALL BATTERIES
# =========================================================

@router.get("/")
def get_batteries(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            id,
            battery_number
        FROM batteries
        ORDER BY battery_number
    """)

    result = db.execute(query).mappings().all()

    batteries = []

    for row in result:

        batteries.append({
            "id": row["id"],
            "battery_number": row["battery_number"]
        })

    return {
        "data": batteries
    }

# =========================================================
# GET COMPLETE BATTERY HISTORY
# =========================================================

@router.get("/{battery_number}/history")
def get_battery_history(
    battery_number: int,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # CHECK WHETHER BATTERY EXISTS
    # -----------------------------------------------------

    battery_query = text("""
        SELECT
            id,
            battery_number
        FROM batteries
        WHERE battery_number = :battery_number
    """)

    battery_result = db.execute(
        battery_query,
        {
            "battery_number": battery_number
        }
    ).fetchone()


    if battery_result is None:

        raise HTTPException(
            status_code=404,
            detail=f"Battery {battery_number} was not found."
        )


    # -----------------------------------------------------
    # GET HISTORY
    # -----------------------------------------------------

    query = text("""
        SELECT
            dr.id,
            dr.delay_date,
            dr.shift,
            b.battery_number,
            m.machine_name,
            me.mechanism_name,
            a.agency_name,
            dr.start_time,
            dr.end_time,
            dr.delay_minutes,
            dr.attended,
            dr.remark

        FROM delay_records dr

        JOIN delay_batteries db
            ON dr.id = db.delay_id

        JOIN batteries b
            ON db.battery_id = b.id

        JOIN machines m
            ON dr.machine_id = m.id

        JOIN mechanisms me
            ON dr.mechanism_id = me.id

        JOIN agencies a
            ON dr.agency_id = a.id

        WHERE b.battery_number = :battery_number

        ORDER BY
            dr.delay_date,
            dr.start_time
    """)


    result = db.execute(
        query,
        {
            "battery_number": battery_number
        }
    )


    records = []


    for row in result:

        records.append({

            "id": row.id,

            "date": str(
                row.delay_date
            ),

            "shift": row.shift,

            "battery": row.battery_number,

            "machine": row.machine_name,

            "mechanism": row.mechanism_name,

            "agency": row.agency_name,

            "start_time": str(
                row.start_time
            ),

            "end_time": str(
                row.end_time
            ),

            "delay_minutes":
                row.delay_minutes,

            "delay_hours":
                round(
                    row.delay_minutes / 60,
                    2
                ),

            "attended":
                row.attended,

            "remark":
                row.remark
        })


    # -----------------------------------------------------
    # TOTALS
    # -----------------------------------------------------

    total_delay = sum(
        record["delay_minutes"]
        for record in records
    )


    total_delay_hours = round(
        total_delay / 60,
        2
    )


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "battery":
            battery_number,

        "total_records":
            len(records),

        "total_delay_minutes":
            total_delay,

        "total_delay_hours":
            total_delay_hours,

        "records":
            records
    }