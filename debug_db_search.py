from app.db.database import engine
from sqlalchemy import inspect, text

inspector = inspect(engine)
search = 'abhay.1plusbackup@gmail.com'

with engine.connect() as conn:
    print(f"Searching for '{search}' in all tables...")
    for table_name in inspector.get_table_names():
        try:
            res = conn.execute(text(f'SELECT * FROM "{table_name}"'))
            cols = res.keys()
            for row in res:
                for val in row:
                    if val and str(val).lower() == search.lower():
                        print(f"\n--- MATCH FOUND ---")
                        print(f"Table: {table_name}")
                        data = dict(zip(cols, row))
                        print(data)
        except Exception as e:
            pass
print("\nSearch complete.")
