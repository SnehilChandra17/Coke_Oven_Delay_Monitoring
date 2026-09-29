from sqlalchemy import text

from database import engine


print("Testing MySQL connection...")

try:

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT VERSION()")
        )

        version = result.fetchone()[0]

        print("MySQL connection successful!")
        print("MySQL version:", version)

except Exception as e:

    print("MySQL connection failed!")
    print("Error:", e)