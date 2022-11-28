import psycopg2 as db

def connect():
    conn=db.connect(host="db",user="myprojectuser",password="password",database='postgres',port=5432)
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
    conn.commit()

manualTable()
