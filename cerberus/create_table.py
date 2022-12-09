import psycopg2 as db
from datetime import date

def connect():
    conn=db.connect(host="localhost",user="postgres",password="1234",database='battery_management')
    return conn


def manualTable():
    conn=connect()
    cursor = conn.cursor()
    sql = "CREATE TABLE IF NOT EXISTS public.user_management_organisation_user_role_one \
    ( \
        email VARCHAR(255) NOT NULL, \
        serial_number VARCHAR(255) NOT NULL, \
        id VARCHAR(200) NOT NULL, \
        user_status boolean)"
    cursor.execute(sql)
    print("Table is creted")
    conn.commit()

manualTable()

def AdminCreate():
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = "INSERT INTO irasusapp_crmuser(username, email, contact, password, password_conformation, is_admin, is_active, last_login,created_at,updated_at,deleted_at,user_type) \
        VALUES ('admin','admin@gmail.com','7041999864','Admin@123','Admin@123','True','True','2022-12-09 06:58:35.943724+05:30','2022-12-09 06:58:35.943724+05:30','2022-12-09 06:58:35.943724+05:30','2022-12-09 06:58:35.943724+05:30','Admin');"
        cursor.execute(sql)
        conn.commit()
        print("done")
        cursor.close()
        return
    except Exception as e:
        print(e) 

AdminCreate()