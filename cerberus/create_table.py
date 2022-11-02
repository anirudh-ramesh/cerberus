import psycopg2 as db

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
        user_status boolean, \
        FOREIGN KEY(email) REFERENCES irasusapp_crmuser (email), \
        FOREIGN KEY(serial_number) REFERENCES user_management_organisation (serial_number))"
    cursor.execute(sql)
    conn.commit()

manualTable()
