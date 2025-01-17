import mysql.connector
import json
import os

def load_config():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)

def get_connection():
    c = load_config()
    return mysql.connector.connect(
        host=c["host"],
        user=c["user"],
        password=c["password"],
        database=c["database"]
    )

def execute_query(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
    except mysql.connector.Error as e:
        conn.rollback()
        raise Exception(f"Chyba SQL: {e}")
    finally:
        cur.close()
        conn.close()

def fetch_all(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        return cur.fetchall()
    except mysql.connector.Error as e:
        raise Exception(f"Chyba SELECT: {e}")
    finally:
        cur.close()
        conn.close()
