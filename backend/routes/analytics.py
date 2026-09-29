from datetime import date as DateType

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import get_db


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


# ---------------------------------------------------------
# OVERALL SUMMARY
# ---------------------------------------------------------

@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            COUNT(*) AS total_records,
            COALESCE(SUM(delay_minutes), 0) AS total_delay_minutes,
            COALESCE(AVG(delay_minutes), 0) AS average_delay_minutes
        FROM delay_records
    """)

    result = db.execute(query).fetchone()

    total_delay = int(result.total_delay_minutes)

    return {
        "total_records": int(result.total_records),
        "total_delay_minutes": total_delay,
        "total_delay_hours": round(total_delay / 60, 2),
        "average_delay_minutes": round(
            float(result.average_delay_minutes), 2
        )
    }


# ---------------------------------------------------------
# DELAY BY MACHINE
# ---------------------------------------------------------

@router.get("/machine")
def get_machine_analytics(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            m.machine_name,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes) AS total_delay_minutes
        FROM delay_records dr

        JOIN machines m
            ON dr.machine_id = m.id

        GROUP BY
            m.machine_name

        ORDER BY
            total_delay_minutes DESC
    """)

    result = db.execute(query)

    records = []

    for row in result:

        records.append({
            "machine": row.machine_name,
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            ),
            "total_delay_hours": round(
                int(row.total_delay_minutes) / 60,
                2
            )
        })

    return {
        "data": records
    }


# ---------------------------------------------------------
# DELAY BY MECHANISM
# ---------------------------------------------------------

@router.get("/mechanism")
def get_mechanism_analytics(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            me.mechanism_name,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes) AS total_delay_minutes
        FROM delay_records dr

        JOIN mechanisms me
            ON dr.mechanism_id = me.id

        GROUP BY
            me.mechanism_name

        ORDER BY
            total_delay_minutes DESC
    """)

    result = db.execute(query)

    records = []

    for row in result:

        records.append({
            "mechanism": row.mechanism_name,
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            )
        })

    return {
        "data": records
    }


# ---------------------------------------------------------
# DELAY BY AGENCY
# ---------------------------------------------------------

@router.get("/agency")
def get_agency_analytics(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            a.agency_name,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes) AS total_delay_minutes
        FROM delay_records dr

        JOIN agencies a
            ON dr.agency_id = a.id

        GROUP BY
            a.agency_name

        ORDER BY
            total_delay_minutes DESC
    """)

    result = db.execute(query)

    records = []

    for row in result:

        records.append({
            "agency": row.agency_name,
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            )
        })

    return {
        "data": records
    }


# ---------------------------------------------------------
# DELAY BY SHIFT
# ---------------------------------------------------------

@router.get("/shift")
def get_shift_analytics(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            shift,
            COUNT(*) AS record_count,
            SUM(delay_minutes) AS total_delay_minutes
        FROM delay_records

        GROUP BY
            shift

        ORDER BY
            shift
    """)

    result = db.execute(query)

    records = []

    for row in result:

        records.append({
            "shift": row.shift,
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            )
        })

    return {
        "data": records
    }


# ---------------------------------------------------------
# DELAY BY BATTERY
# ---------------------------------------------------------

@router.get("/battery")
def get_battery_analytics(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            b.battery_number,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes) AS total_delay_minutes
        FROM delay_records dr

        JOIN delay_batteries db
            ON dr.id = db.delay_id

        JOIN batteries b
            ON db.battery_id = b.id

        GROUP BY
            b.battery_number

        ORDER BY
            total_delay_minutes DESC
    """)

    result = db.execute(query)

    records = []

    for row in result:

        records.append({
            "battery": row.battery_number,
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            ),
            "total_delay_hours": round(
                int(row.total_delay_minutes) / 60,
                2
            )
        })

    return {
        "data": records
    }


# ---------------------------------------------------------
# DATE-RANGE ANALYTICS
# ---------------------------------------------------------

@router.get("/date-range")
def get_date_range_analytics(
    start_date: DateType = Query(
        ...,
        description="Start date in YYYY-MM-DD format"
    ),
    end_date: DateType = Query(
        ...,
        description="End date in YYYY-MM-DD format"
    ),
    db: Session = Depends(get_db)
):

    # ---------------------------------------------
    # Validate date range
    # ---------------------------------------------

    if start_date > end_date:
        return {
            "error": "start_date cannot be later than end_date."
        }

    # ---------------------------------------------
    # Overall filtered summary
    # ---------------------------------------------

    summary_query = text("""
        SELECT
            COUNT(*) AS total_records,
            COALESCE(SUM(delay_minutes), 0)
                AS total_delay_minutes,
            COALESCE(AVG(delay_minutes), 0)
                AS average_delay_minutes
        FROM delay_records
        WHERE delay_date BETWEEN :start_date AND :end_date
    """)

    summary = db.execute(
        summary_query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    ).fetchone()

    total_delay = int(summary.total_delay_minutes)

    # ---------------------------------------------
    # Delay by date
    # ---------------------------------------------

    date_query = text("""
        SELECT
            delay_date,
            COUNT(*) AS record_count,
            SUM(delay_minutes) AS total_delay_minutes
        FROM delay_records
        WHERE delay_date BETWEEN :start_date AND :end_date
        GROUP BY delay_date
        ORDER BY delay_date
    """)

    date_result = db.execute(
        date_query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    )

    by_date = []

    for row in date_result:

        by_date.append({
            "date": str(row.delay_date),
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            ),
            "total_delay_hours": round(
                int(row.total_delay_minutes) / 60,
                2
            )
        })

    # ---------------------------------------------
    # Delay by shift
    # ---------------------------------------------

    shift_query = text("""
        SELECT
            shift,
            COUNT(*) AS record_count,
            SUM(delay_minutes) AS total_delay_minutes
        FROM delay_records
        WHERE delay_date BETWEEN :start_date AND :end_date
        GROUP BY shift
        ORDER BY shift
    """)

    shift_result = db.execute(
        shift_query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    )

    by_shift = []

    for row in shift_result:

        by_shift.append({
            "shift": row.shift,
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            ),
            "total_delay_hours": round(
                int(row.total_delay_minutes) / 60,
                2
            )
        })

    # ---------------------------------------------
    # Delay by machine
    # ---------------------------------------------

    machine_query = text("""
        SELECT
            m.machine_name,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes) AS total_delay_minutes
        FROM delay_records dr
        JOIN machines m
            ON dr.machine_id = m.id
        WHERE dr.delay_date BETWEEN :start_date AND :end_date
        GROUP BY m.machine_name
        ORDER BY total_delay_minutes DESC
    """)

    machine_result = db.execute(
        machine_query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    )

    by_machine = []

    for row in machine_result:

        by_machine.append({
            "machine": row.machine_name,
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            ),
            "total_delay_hours": round(
                int(row.total_delay_minutes) / 60,
                2
            )
        })

    # ---------------------------------------------
    # Delay by mechanism
    # ---------------------------------------------

    mechanism_query = text("""
        SELECT
            me.mechanism_name,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes) AS total_delay_minutes
        FROM delay_records dr
        JOIN mechanisms me
            ON dr.mechanism_id = me.id
        WHERE dr.delay_date BETWEEN :start_date AND :end_date
        GROUP BY me.mechanism_name
        ORDER BY total_delay_minutes DESC
    """)

    mechanism_result = db.execute(
        mechanism_query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    )

    by_mechanism = []

    for row in mechanism_result:

        by_mechanism.append({
            "mechanism": row.mechanism_name,
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            ),
            "total_delay_hours": round(
                int(row.total_delay_minutes) / 60,
                2
            )
        })

    # ---------------------------------------------
    # Delay by agency
    # ---------------------------------------------

    agency_query = text("""
        SELECT
            a.agency_name,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes) AS total_delay_minutes
        FROM delay_records dr
        JOIN agencies a
            ON dr.agency_id = a.id
        WHERE dr.delay_date BETWEEN :start_date AND :end_date
        GROUP BY a.agency_name
        ORDER BY total_delay_minutes DESC
    """)

    agency_result = db.execute(
        agency_query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    )

    by_agency = []

    for row in agency_result:

        by_agency.append({
            "agency": row.agency_name,
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            ),
            "total_delay_hours": round(
                int(row.total_delay_minutes) / 60,
                2
            )
        })


    # ---------------------------------------------
    # Delay by battery
    # ---------------------------------------------

    battery_query = text("""
        SELECT
            b.battery_number,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes) AS total_delay_minutes
        FROM delay_records dr
        JOIN delay_batteries db
            ON dr.id = db.delay_id
        JOIN batteries b
            ON db.battery_id = b.id
        WHERE dr.delay_date BETWEEN :start_date AND :end_date
        GROUP BY b.battery_number
        ORDER BY total_delay_minutes DESC
    """)

    battery_result = db.execute(
        battery_query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    )

    by_battery = []

    for row in battery_result:

        by_battery.append({
            "battery": row.battery_number,
            "record_count": int(row.record_count),
            "total_delay_minutes": int(
                row.total_delay_minutes
            ),
            "total_delay_hours": round(
                int(row.total_delay_minutes) / 60,
                2
            )
        })

    # ---------------------------------------------
    # FINAL RESPONSE
    # ---------------------------------------------

    return {
        "start_date": str(start_date),
        "end_date": str(end_date),

        "summary": {
            "total_records": int(summary.total_records),
            "total_delay_minutes": total_delay,
            "total_delay_hours": round(
                total_delay / 60,
                2
            ),
            "average_delay_minutes": round(
                float(summary.average_delay_minutes),
                2
            )
        },

        "by_date": by_date,
        "by_shift": by_shift,
        "by_machine": by_machine,
        "by_mechanism": by_mechanism,
        "by_agency": by_agency,
        "by_battery": by_battery
    }

# =========================================================
# FILTERED ANALYTICS
# =========================================================

@router.get("/filtered")
def get_filtered_analytics(
    start_date: DateType = Query(
        ...,
        description="Start date in YYYY-MM-DD format"
    ),
    end_date: DateType = Query(
        ...,
        description="End date in YYYY-MM-DD format"
    ),
    battery: int | None = Query(
        None,
        gt=0,
        description="Optional battery number"
    ),
    machine: str | None = Query(
        None,
        description="Optional machine name"
    ),
    agency: str | None = Query(
        None,
        description="Optional agency name"
    ),
    shift: str | None = Query(
        None,
        description="Optional shift: A, B, or C"
    ),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # VALIDATE DATE RANGE
    # -----------------------------------------------------

    if start_date > end_date:
        return {
            "error": "start_date cannot be later than end_date."
        }


    # -----------------------------------------------------
    # BUILD FILTER CONDITIONS
    # -----------------------------------------------------

    conditions = [
        "dr.delay_date BETWEEN :start_date AND :end_date"
    ]

    params = {
        "start_date": start_date,
        "end_date": end_date
    }


    # Battery filter
    if battery is not None:

        conditions.append("""
            EXISTS (
                SELECT 1
                FROM delay_batteries filter_db
                JOIN batteries filter_b
                    ON filter_db.battery_id = filter_b.id
                WHERE filter_db.delay_id = dr.id
                  AND filter_b.battery_number = :battery
            )
        """)

        params["battery"] = battery


    # Machine filter
    if machine:

        conditions.append(
            "m.machine_name = :machine"
        )

        params["machine"] = machine


    # Agency filter
    if agency:

        conditions.append(
            "a.agency_name = :agency"
        )

        params["agency"] = agency


    # Shift filter
    if shift:

        shift = shift.upper()

        if shift not in ["A", "B", "C"]:

            return {
                "error": "Shift must be A, B, or C."
            }

        conditions.append(
            "dr.shift = :shift"
        )

        params["shift"] = shift


    where_clause = " AND ".join(
        conditions
    )


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    summary_query = text(f"""
        SELECT
            COUNT(*) AS total_records,
            COALESCE(
                SUM(dr.delay_minutes),
                0
            ) AS total_delay_minutes,
            COALESCE(
                AVG(dr.delay_minutes),
                0
            ) AS average_delay_minutes

        FROM delay_records dr

        JOIN machines m
            ON dr.machine_id = m.id

        JOIN agencies a
            ON dr.agency_id = a.id

        WHERE {where_clause}
    """)


    summary = db.execute(
        summary_query,
        params
    ).fetchone()


    total_delay = int(
        summary.total_delay_minutes
    )


    # -----------------------------------------------------
    # BY DATE
    # -----------------------------------------------------

    date_query = text(f"""
        SELECT
            dr.delay_date,
            COUNT(*) AS record_count,
            SUM(dr.delay_minutes)
                AS total_delay_minutes

        FROM delay_records dr

        JOIN machines m
            ON dr.machine_id = m.id

        JOIN agencies a
            ON dr.agency_id = a.id

        WHERE {where_clause}

        GROUP BY dr.delay_date

        ORDER BY dr.delay_date
    """)


    date_result = db.execute(
        date_query,
        params
    )


    by_date = []


    for row in date_result:

        minutes = int(
            row.total_delay_minutes
        )

        by_date.append({
            "date": str(row.delay_date),
            "record_count": int(
                row.record_count
            ),
            "total_delay_minutes": minutes,
            "total_delay_hours": round(
                minutes / 60,
                2
            )
        })


    # -----------------------------------------------------
    # BY SHIFT
    # -----------------------------------------------------

    shift_query = text(f"""
        SELECT
            dr.shift,
            COUNT(*) AS record_count,
            SUM(dr.delay_minutes)
                AS total_delay_minutes

        FROM delay_records dr

        JOIN machines m
            ON dr.machine_id = m.id

        JOIN agencies a
            ON dr.agency_id = a.id

        WHERE {where_clause}

        GROUP BY dr.shift

        ORDER BY dr.shift
    """)


    shift_result = db.execute(
        shift_query,
        params
    )


    by_shift = []


    for row in shift_result:

        minutes = int(
            row.total_delay_minutes
        )

        by_shift.append({
            "shift": row.shift,
            "record_count": int(
                row.record_count
            ),
            "total_delay_minutes": minutes,
            "total_delay_hours": round(
                minutes / 60,
                2
            )
        })


    # -----------------------------------------------------
    # BY MACHINE
    # -----------------------------------------------------

    machine_query = text(f"""
        SELECT
            m.machine_name,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes)
                AS total_delay_minutes

        FROM delay_records dr

        JOIN machines m
            ON dr.machine_id = m.id

        JOIN agencies a
            ON dr.agency_id = a.id

        WHERE {where_clause}

        GROUP BY m.machine_name

        ORDER BY total_delay_minutes DESC
    """)


    machine_result = db.execute(
        machine_query,
        params
    )


    by_machine = []


    for row in machine_result:

        minutes = int(
            row.total_delay_minutes
        )

        by_machine.append({
            "machine": row.machine_name,
            "record_count": int(
                row.record_count
            ),
            "total_delay_minutes": minutes,
            "total_delay_hours": round(
                minutes / 60,
                2
            )
        })


    # -----------------------------------------------------
    # BY MECHANISM
    # -----------------------------------------------------

    mechanism_query = text(f"""
        SELECT
            me.mechanism_name,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes)
                AS total_delay_minutes

        FROM delay_records dr

        JOIN machines m
            ON dr.machine_id = m.id

        JOIN agencies a
            ON dr.agency_id = a.id

        JOIN mechanisms me
            ON dr.mechanism_id = me.id

        WHERE {where_clause}

        GROUP BY me.mechanism_name

        ORDER BY total_delay_minutes DESC
    """)


    mechanism_result = db.execute(
        mechanism_query,
        params
    )


    by_mechanism = []


    for row in mechanism_result:

        minutes = int(
            row.total_delay_minutes
        )

        by_mechanism.append({
            "mechanism": row.mechanism_name,
            "record_count": int(
                row.record_count
            ),
            "total_delay_minutes": minutes,
            "total_delay_hours": round(
                minutes / 60,
                2
            )
        })


    # -----------------------------------------------------
    # BY AGENCY
    # -----------------------------------------------------

    agency_query = text(f"""
        SELECT
            a.agency_name,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes)
                AS total_delay_minutes

        FROM delay_records dr

        JOIN machines m
            ON dr.machine_id = m.id

        JOIN agencies a
            ON dr.agency_id = a.id

        WHERE {where_clause}

        GROUP BY a.agency_name

        ORDER BY total_delay_minutes DESC
    """)


    agency_result = db.execute(
        agency_query,
        params
    )


    by_agency = []


    for row in agency_result:

        minutes = int(
            row.total_delay_minutes
        )

        by_agency.append({
            "agency": row.agency_name,
            "record_count": int(
                row.record_count
            ),
            "total_delay_minutes": minutes,
            "total_delay_hours": round(
                minutes / 60,
                2
            )
        })


    # -----------------------------------------------------
    # BY BATTERY
    # -----------------------------------------------------

    battery_query = text(f"""
        SELECT
            b.battery_number,
            COUNT(dr.id) AS record_count,
            SUM(dr.delay_minutes)
                AS total_delay_minutes

        FROM delay_records dr

        JOIN machines m
            ON dr.machine_id = m.id

        JOIN agencies a
            ON dr.agency_id = a.id

        JOIN delay_batteries db
            ON dr.id = db.delay_id

        JOIN batteries b
            ON db.battery_id = b.id

        WHERE {where_clause}

        GROUP BY b.battery_number

        ORDER BY total_delay_minutes DESC
    """)


    battery_result = db.execute(
        battery_query,
        params
    )


    by_battery = []


    for row in battery_result:

        minutes = int(
            row.total_delay_minutes
        )

        by_battery.append({
            "battery": row.battery_number,
            "record_count": int(
                row.record_count
            ),
            "total_delay_minutes": minutes,
            "total_delay_hours": round(
                minutes / 60,
                2
            )
        })

    # -----------------------------------------------------
    # BY ATTENDED STATUS
    # -----------------------------------------------------

    attended_query = text(f"""
        SELECT
            dr.attended,
            COUNT(*) AS record_count,
            SUM(dr.delay_minutes) AS total_delay_minutes

        FROM delay_records dr

        JOIN machines m
            ON dr.machine_id = m.id

        JOIN agencies a
            ON dr.agency_id = a.id

        WHERE {where_clause}

        GROUP BY dr.attended

        ORDER BY total_delay_minutes DESC
    """)

    attended_result = db.execute(
        attended_query,
        params
    )

    by_attended = []

    for row in attended_result:

        minutes = int(
            row.total_delay_minutes
        )

        by_attended.append({
            "attended": row.attended,
            "record_count": int(
                row.record_count
            ),
            "total_delay_minutes": minutes,
            "total_delay_hours": round(
                minutes / 60,
                2
            )
        })

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    return {

        "filters": {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "battery": battery,
            "machine": machine,
            "agency": agency,
            "shift": shift
        },

        "summary": {

            "total_records": int(
                summary.total_records
            ),

            "total_delay_minutes":
                total_delay,

            "total_delay_hours":
                round(
                    total_delay / 60,
                    2
                ),

            "average_delay_minutes":
                round(
                    float(
                        summary.average_delay_minutes
                    ),
                    2
                )
        },

        "by_date": by_date,
        "by_shift": by_shift,
        "by_machine": by_machine,
        "by_mechanism": by_mechanism,
        "by_agency": by_agency,
        "by_battery": by_battery,
        "by_attended": by_attended
        
    }
