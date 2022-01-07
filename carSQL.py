import datetime

from psycopg2 import sql
import psycopg2.extras

DB_HOST = "localhost"
DB_NAME = "carsystem"
DB_USER = "postgres"
DB_PASS = "postgres"
conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
default_date = datetime.date(1970,1,1)

def login_query(tablename=None):
    if tablename is None:
        tablename = 'customer'
    return sql.SQL("SELECT * FROM {table} WHERE username = %s").format(table=sql.Identifier(tablename))


customer_register = "INSERT INTO customer (username, password, fname, lname, email, country, city, address) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
admin_register = "INSERT INTO admin (username, password) VALUES (%s,%s)"
car_register = "INSERT INTO car (plateid,modelyr,brand,model,color,rate) VALUES (%s,%s,%s,%s,%s,%s)"
car_image_register = "INSERT INTO car_image (plateid, image) values (%s,%s)"
car_search = "SELECT car.* , car_image.image FROM car natural join car_image WHERE " \
             "plateid = %s or modelyr = %s or brand = %s or model=%s or color=%s or active = %s or rate = %s"
car_search_customer = "SELECT car.* , car_image.image FROM car natural join car_image WHERE " \
             "plateid = %s or modelyr = %s or brand = %s or model=%s or color=%s or rate = %s and active = %s"

car_search_plate = "SELECT car.* , car_image.image FROM car natural join car_image WHERE plateid = %s "
update_car = "UPDATE car SET (active,rate) = (%s,%s) WHERE plateid = %s"
