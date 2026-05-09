import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def execute_sql_file(user, password, host="localhost", port="5432"):
    conn = None
    try:
        # 1. Connect to the database
        conn = psycopg2.connect(
            dbname="postgres", user=user, password=password, host=host, port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # 2. Create the database
        try:
            cursor.execute(f"CREATE DATABASE logs")
            print(f"Database logs created.")
        except psycopg2.errors.DuplicateDatabase:
            print(f"Database logs already exists.")
        
        cursor.close()
        conn.close()

        # 3. NOW connect to the new database to run your schema
        conn = psycopg2.connect(dbname="logs", user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        # 2. Open and read the SQL file
        with open("/databse.sql", 'r') as sql_file:
            sql_script = sql_file.read()

        # 3. Execute the script
        # psycopg2 handles multiple statements separated by ';' automatically
        cursor.execute(sql_script)
        
        # 4. Commit changes
        conn.commit()
        print("SQL script executed successfully.")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while running script: {error}")
    finally:
        # 5. Clean up connection
        if conn is not None:
            cursor.close()
            conn.close()
    
execute_sql_file("postgres", "Riley@225", host="localhost", port="5432")