from psycopg2 import sql
import psycopg2.extras

DB_HOST = "localhost"
DB_NAME = "carsystem"
DB_USER = "postgres"
DB_PASS = "postgres"
conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def login_query(tablename=None):
    if tablename is None:
        tablename = 'customer'
    return sql.SQL("SELECT * FROM {table} WHERE username = %s").format(table=sql.Identifier(tablename))


customer_register = "INSERT INTO customer (username, password, fname, lname, email, country, city, address) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
