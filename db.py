import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": ""   # yaha apna MySQL password daal
}


def create_database_and_table():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS web_spam")
    cursor.execute("USE web_spam")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(150),
            mobile VARCHAR(20),
            dob VARCHAR(30),
            gender VARCHAR(20),
            subject VARCHAR(100),
            hobbies VARCHAR(200),
            address TEXT,
            state VARCHAR(100),
            city VARCHAR(100),
            score FLOAT,
            verdict VARCHAR(20),
            rules_triggered TEXT,
            collected_at VARCHAR(50)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # yaha bhi same password daal
        database="web_spam"
    )


def init_db():
    create_database_and_table()


def insert_submission(first_name, last_name, email, mobile, dob, gender, subject,
                      hobbies, address, state, city, score, verdict,
                      rules_triggered, collected_at):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO submissions (
            first_name, last_name, email, mobile, dob, gender, subject,
            hobbies, address, state, city, score, verdict, rules_triggered, collected_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        first_name, last_name, email, mobile, dob, gender, subject,
        hobbies, address, state, city, score, verdict, rules_triggered, collected_at
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database 'web_spam' and table 'submissions' created successfully.")