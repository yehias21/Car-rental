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
admin_register = "INSERT INTO admin (username, password) VALUES (%s,%s)"
car_register = "INSERT INTO car (plateid,modelyr,brand,model,color) VALUES (%s,%s,%s,%s,%s)"
car_image_register = "INSERT INTO car_image (plateid, image) values (%s,%s)"
