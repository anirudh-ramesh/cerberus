import psycopg2 as db
import os
from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv())


def connect():
    conn=db.connect(host= os.getenv('HOST'),user=os.getenv('USER_NAME'),password=os.getenv('PASSWORD'),database=os.getenv('DATABASE_NAME'))
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
        VALUES ('admin','dixit.ims.in@gmail.com','7041999864','pbkdf2_sha256$390000$UnohK4YrmvOt9W5PeqWLG8$7QzSegy5en47+dI0uLq+4hrAlsOSDUi2OUhnm+k0ruk=','pbkdf2_sha256$390000$UnohK4YrmvOt9W5PeqWLG8$7QzSegy5en47+dI0uLq+4hrAlsOSDUi2OUhnm+k0ruk=','True','True','2022-12-09 06:58:35.943724+05:30','2022-12-09 06:58:35.943724+05:30','2022-12-09 06:58:35.943724+05:30','2022-12-09 06:58:35.943724+05:30','Admin');"
        cursor.execute(sql)
        conn.commit()
        print("done")
        sql="select * from irasusapp_crmuser;"
        cursor.execute(sql)
        print(cursor.fetchall())
        cursor.close()
        return
    except Exception as e:
        print(e) 

AdminCreate()