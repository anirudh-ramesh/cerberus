import psycopg2 as db

def connect():
    conn=db.connect(host="localhost",user="postgres",password="1234",database='battery_management')
    return conn
    
def sql_query(id):
    conn=connect()
    cursor=conn.cursor()
    sql= f"SELECT email FROM irasusapp_crmuser WHERE NOT EXISTS (SELECT email,serial_number FROM user_management_organisation_user_role WHERE user_management_organisation_user_role.serial_nuOrganisationPermissionmber = '{id}' AND irasusapp_crmuser.email = user_management_organisation_user_role.email) AND irasusapp_crmuser.is_admin=True;"
    cursor.execute(sql)
    myresult = cursor.fetchall()
    new_data=[]
    for data in myresult:
        new_data.append(data[0])
    cursor.close()    
    return new_data

def inset_into_db(data,id,role):
    conn=connect()
    cursor=conn.cursor()
    query = 'INSERT INTO user_management_organisation_user_role(serial_number,email,id) \
    VALUES(%s,%s,%s) '                                                         
    my_data = []
    for row in data:
        my_data.append((id,row,str(role)))
    cursor.executemany(query, my_data)
    conn.commit()
    cursor.close()
    return 


def getOrgUserInfo(id):
    conn=connect()

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


def orgProfileAddData(id,orgprofile_id):
    conn=connect()
    cursor = conn.cursor()
    sql = 'INSERT INTO user_management_organisation_organisation_profile(organisation_id,organisationprofile_id) \
    VALUES(%s,%s)'
    my_data = (id,orgprofile_id)
    cursor.execute(sql, my_data)
    conn.commit()
    cursor.close()
    return

def getOrgProfiles(id):
    conn=connect()
    cursor=conn.cursor()
    sql = f"SELECT \
    * \
    FROM user_management_organisationprofile \
    LEFT JOIN user_management_organisation_organisation_profile ON user_management_organisationprofile.id = user_management_organisation_organisation_profile.organisationprofile_id \
    WHERE user_management_organisation_organisation_profile.organisation_id='{id}'"
    cursor.execute(sql)
    myresult = cursor.fetchall()
    new_data = []
    for row in myresult:
        res={}
        print(row[2])
        res["battery_pack_manufacture"] = str(row[1])
        res["battery_pack_distributor"] = row[2]
        res["battery_pack_sub_distributor"] = row[3]
        res["battery_pack_financier"] = row[4]
        res["battery_pack_owner"] = row[5]
        res["battery_pack_operator"] = row[6]
        res["vehical_manufacture"] = row[7]
        res["vehical_distributor"] = row[8]
        res["vehical_sub_distributor"] = row[9]
        res["vehical_retailer"] = row[10]
        res["vehical_financier"] = row[11]
        res["vehical_owner"] = row[12]
        res["vehical_operator"] = row[13]
        res["battrey_swap_satation_manufacture"] = row[14]
        res["battrey_swap_satation_distributor"] = row[15]
        res["battrey_swap_satation_sub_distributor"] = row[16]
        res["battrey_swap_satation_financier"] = row[17]
        res["battrey_swap_satation_owner"] = row[18]
        res["battrey_swap_satation_operator"] = row[19]
        new_data.append(res)
    cursor.close()
    return new_data

def getOrgRoles(id):
    conn=connect()
    cursor=conn.cursor()
    sql = f"SELECT \
    * \
    FROM user_management_role \
    LEFT JOIN user_management_organisation_organisation_profile ON user_management_role.id = user_management_organisation_organisation_profile.organisationprofile_id \
    WHERE user_management_organisation_organisation_profile.organisation_id='{id}'"
    cursor.execute(sql)
    myresult = cursor.fetchall()
    new_data = []
    for row in myresult:
        res={}
        print(row[2])
        res["battery_pack_manufacture"] = str(row[1])
        res["battery_pack_distributor"] = row[2]
        res["battery_pack_sub_distributor"] = row[3]
        res["battery_pack_financier"] = row[4]
        res["battery_pack_owner"] = row[5]
        res["battery_pack_operator"] = row[6]
        res["vehical_manufacture"] = row[7]
        res["vehical_distributor"] = row[8]
        res["vehical_sub_distributor"] = row[9]
        res["vehical_retailer"] = row[10]
        res["vehical_financier"] = row[11]
        res["vehical_owner"] = row[12]
        res["vehical_operator"] = row[13]
        res["battrey_swap_satation_manufacture"] = row[14]
        res["battrey_swap_satation_distributor"] = row[15]
        res["battrey_swap_satation_sub_distributor"] = row[16]
        res["battrey_swap_satation_financier"] = row[17]
        res["battrey_swap_satation_owner"] = row[18]
        res["battrey_swap_satation_operator"] = row[19]
        new_data.append(res)
    cursor.close()
    return new_data

def orgUserUpdateData(role,serial_number,email):
    conn=connect()
    cursor = conn.cursor()
    sql = f"UPDATE user_management_organisation_user_role set id='{role}' WHERE serial_number ='{serial_number}' AND email='{email}';"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    return

def organisationmultiplePermission(id):
    conn=connect()
    cursor=conn.cursor()
    sql = f"SELECT \
    user_management_organisationpermission.permission_name, user_management_organisationpermission.role_name, user_management_organisationpermission.role_id \
    FROM user_management_role \
    RIGHT JOIN user_management_organisationpermission ON user_management_organisationpermission.role_id = user_management_role.id \
    WHERE user_management_role.org_id='{id}'"
    cursor.execute(sql)
    myresult = cursor.fetchall()
    my_data = []
    role_name=[]
    for row in myresult:
        res={}
        if(len(role_name) != 0 and row[1] in role_name):
            index_data=role_name.index(row[1])
            my_data[index_data]["permission_name"]=my_data[index_data]["permission_name"] + [row[0]]
        else:    
            res['permission_name'] = [row[0]]
            res['role_name'] = row[1]
            res['role_id'] = row[2]
            my_data.append(res)
            role_name.append(row[1])
    return my_data

def insertIntoOrgnisationPermission(permission_name,role_name,role_id):
    conn=connect()
    cursor = conn.cursor()
    sql = 'INSERT INTO user_management_organisationpermission(permission_name,role_name,role_id) \
    VALUES(%s,%s,%s)'
    my_data = (permission_name,role_name,role_id)
    cursor.execute(sql, my_data)
    conn.commit()
    cursor.close()
    return