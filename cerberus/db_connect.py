import psycopg2 as db

def sql_query(id):
    conn=db.connect(host="localhost",user="postgres",password="1234",database='battery_management')
    cursor=conn.cursor()
    sql= f"SELECT email FROM irasusapp_crmuser WHERE NOT EXISTS (SELECT email,serial_number FROM user_management_organisation_user_role WHERE user_management_organisation_user_role.serial_number = '{id}' AND irasusapp_crmuser.email = user_management_organisation_user_role.email);"
    cursor.execute(sql)
    myresult = cursor.fetchall()
    new_data=[]
    for data in myresult:
        new_data.append(data[0])
    cursor.close()    
    return new_data

def inset_into_db(data,id,role):
    conn=db.connect(host="localhost",user="postgres",password="1234",database='battery_management')

    cursor=conn.cursor()
    query = 'INSERT INTO user_management_organisation_user_role(serial_number,email,id) \
    VALUES(%s,%s,%s) '                                                         
    my_data = []
    print(role,"=====")
    for row in data:
        my_data.append((id,row,str(role)))
    cursor.executemany(query, my_data)
    conn.commit()
    cursor.close()
    return 


def getOrgUserInfo(id):
    conn=db.connect(host="localhost",user="postgres",password="1234",database='battery_management')

    cursor=conn.cursor()
    # sql= f"SELECT email,username, FROM irasusapp_crmuser WHERE EXISTS (SELECT email,serial_number,id FROM user_management_organisation_user_role WHERE user_management_organisation_user_role.serial_number = '{id}' AND irasusapp_crmuser.email = user_management_organisation_user_role.email);"
    sql = f"SELECT \
    irasusapp_crmuser.email,irasusapp_crmuser.username,user_management_organisation_user_role.id \
    FROM irasusapp_crmuser \
    LEFT JOIN user_management_organisation_user_role ON irasusapp_crmuser.email = user_management_organisation_user_role.email \
    WHERE user_management_organisation_user_role.serial_number='{id}'"
    cursor.execute(sql)
    myresult = cursor.fetchall()
    my_data = []
    for row in myresult:
        res={}
        print(row)
        res["email"]=row[0]
        res["username"]=row[1]
        res["role"]=row[2]
        my_data.append(res)
    cursor.close()
    return my_data