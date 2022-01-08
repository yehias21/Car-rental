from psycopg2 import sql
import psycopg2.extras

DB_HOST = "localhost"
DB_NAME = "carsystem"
DB_USER = "postgres"
DB_PASS = "postgres"
conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
db = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def login_query(tablename=None):
    if tablename is None:
        tablename = 'customer'
    return sql.SQL("SELECT * FROM {table} WHERE username = %s").format(table=sql.Identifier(tablename))


customer_register = "INSERT INTO customer (username, password, fname, lname, email, country, city, address) VALUES (" \
                    "%s,%s,%s,%s,%s,%s,%s,%s) "
admin_register = "INSERT INTO admin (username, password) VALUES (%s,%s)"
car_register = "INSERT INTO car (plateid,modelyr,brand,model,color,rate) VALUES (%s,%s,%s,%s,%s,%s)"
car_image_register = "INSERT INTO car_image (plateid, image) values (%s,%s)"
car_search = "SELECT car.plateid, extract(year from car.modelyr) as year, brand, model, color, active, rate , " \
             "encode(car_image.image,'hex') img " \
             "FROM car natural join car_image WHERE " \
             "plateid = %s or modelyr = %s or brand = %s or model=%s or color=%s or active = %s or rate = %s"

car_search_plate = "SELECT car.plateid, extract(year from car.modelyr) as year, brand, model, color, active, rate , " \
                   "encode(car_image.image,'hex') img " \
                   "FROM car natural join car_image WHERE plateid = %s "

update_car_rate = "UPDATE car SET rate = %s WHERE plateid = %s"
update_car_state = "UPDATE car SET active = %s::bool WHERE plateid = %s"
car_out_service = "INSERT INTO status(plateid, out_start) values(%s,%s::date) "
car_in_service = "UPDATE status SET out_end = %s WHERE plateid = %s AND out_end IS NULL"

search_customer = "select * from customer where username = %s"

# reports:
all_reservations = "SELECT reserve_date,pickup_date,return_date,concat(fname,lname) customer_name,plateid,bill,paid " \
                   "FROM (reservation join customer c on c.id = reservation.custid) as rc join car on rc.carid = " \
                   "car.plateid " \
                   "where reserve_date between %s and %s "

car_reservations_date = "select reserve_date,pickup_date,return_date,bill,paid from reservation " \
                        "where carid = %s and (reserve_date between %s and %s)"

customer_reservations = "select reserve_date ,pickup_date , return_date , bill ,paid , carid , concat(brand," \
                        "model) car_model " \
                        "from reservation join car c on c.plateid = reservation.carid where custid = %s"

customer_payments = "select carid,reserve_date,amount,date " \
                    "from (payments join customer c on c.id = payments.custid) as cp " \
                    "join reservation r on cp.rid = r.rid where custid = %s"

car_status = "with out_of_service as(select plateid from status where %s::date between out_start and out_end) " \
             "select plateid,'active' as status from car where car.plateid not in (select * from out_of_service) " \
             "union (select plateid,'false' from out_of_service)"
