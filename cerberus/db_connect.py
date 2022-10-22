import psycopg2 as db

def connect():
    conn=db.connect(host="localhost",user="postgres",password="1234",database='battery_management')
    return conn

#List Organisation User  
def sql_query(id):
    conn=connect()
    cursor=conn.cursor()
    sql= f"SELECT email FROM irasusapp_crmuser WHERE NOT EXISTS (SELECT email,serial_number FROM user_management_organisation_user_role WHERE user_management_organisation_user_role.serial_number = '{id}' AND irasusapp_crmuser.email = user_management_organisation_user_role.email);"
    cursor.execute(sql)
    myresult = cursor.fetchall()
    new_data=[]
    for data in myresult:
        new_data.append(data[0])
    cursor.close()    
    return new_data

#Insert User Into Orgnisation
def inset_into_db(data,id,role,select):
    conn=connect()
    cursor=conn.cursor()
    query = 'INSERT INTO user_management_organisation_user_role(serial_number,email,id,user_status) \
    VALUES(%s,%s,%s,%s)'                                                         
    my_data = []
    for row in data:
        my_data.append((id,row,str(role),select))
    cursor.executemany(query, my_data)
    conn.commit()
    cursor.close()
    return 

#List Organisation Info
def getOrgUserInfo(id):
    conn=connect()
    cursor=conn.cursor()
    sql = f"SELECT \
    irasusapp_crmuser.email,irasusapp_crmuser.username,user_management_organisation_user_role.id \
    FROM irasusapp_crmuser \
    LEFT JOIN user_management_organisation_user_role ON irasusapp_crmuser.email = user_management_organisation_user_role.email \
    WHERE user_management_organisation_user_role.serial_number='{id}'AND user_management_organisation_user_role.user_status=True"
    cursor.execute(sql)
    myresult = cursor.fetchall()
    my_data = []
    for row in myresult:
        res={}
        print(row)
        res["email"]=row[0]
        res["username"]=row[1]
        res["role"]=row[2]
        res["id"]=id
        my_data.append(res)
    cursor.close()
    return my_data

#Add Organisation Profile Data
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

#List Organisation Profile
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

#List Organisation Role
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

#Update Organisation User
def orgUserUpdateData(role,serial_number,email):
    conn=connect()
    cursor = conn.cursor()
    sql = f"UPDATE user_management_organisation_user_role set id='{role}' WHERE serial_number ='{serial_number}' AND email='{email}';"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    return

#List Organisation Permission
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

#Insert Organisation Permission
def insertIntoOrgnisationPermission(permission_name,role_name,id):
    conn=connect()
    cursor = conn.cursor()
    sql = 'INSERT INTO user_management_organisationpermission(permission_name,role_name,role_id) \
    VALUES(%s,%s,%s)'
    my_data = (permission_name,role_name,id)
    cursor.execute(sql, my_data)
    conn.commit()
    cursor.close()
    return

#Update Organisation Permission
def updateOrgAssignPermission(permission_name,role_name,id):
    conn=connect()
    cursor = conn.cursor()
    sql = f"UPDATE user_management_organisationpermission set permission_name='{permission_name}', role_name='{role_name}' WHERE id ='{id}';"
    my_data = (permission_name,role_name,id)
    cursor.execute(sql,my_data)
    conn.commit()
    cursor.close()
    return

#Remove User From Organisation
def removeUserFromOrg(select,serial_number,email):
    conn=connect()
    cursor = conn.cursor()
    sql = f"UPDATE user_management_organisation_user_role set user_status='{select}' WHERE serial_number ='{serial_number}' AND email='{email}' ;"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    return

#ASSIGNED BATTERY DATA
def listAssignedBatteryVehicle(id):
    conn=connect()
    cursor = conn.cursor()
    sql = f"SELECT \
    irasusapp_batterydetail.model_name, irasusapp_batterydetail.battery_serial_num, irasusapp_batterydetail.battery_type, \
    irasusapp_batterydetail.bms_type,irasusapp_batterydetail.iot_type,irasusapp_batterydetail.iot_imei_number,irasusapp_batterydetail.sim_number,\
    irasusapp_batterydetail.warrenty_start_date,irasusapp_batterydetail.warrenty_duration, irasusapp_batterydetail.assigned_owner,irasusapp_batterydetail.status,\
    irasusapp_batterydetail.battery_cell_chemistry,irasusapp_batterydetail.battery_pack_nominal_voltage,\
    irasusapp_batterydetail.battery_pack_nominal_charge_capacity, irasusapp_batterydetail.charging_status, irasusapp_batterydetail.vehicle_assign_id,irasusapp_batterydetail.is_assigned\
    FROM irasusapp_batterydetail \
    RIGHT JOIN irasusapp_vehicle ON irasusapp_vehicle.chasis_number = irasusapp_batterydetail.vehicle_assign_id \
    WHERE irasusapp_vehicle.chasis_number='{id}'"
    cursor.execute(sql)
    myresult = cursor.fetchall()
    my_data = []
    for data in myresult:
        res= {}
        res["model_name"] = str(data[0])
        res["battery_serial_num"] = data[1]
        res["battery_type"] = data[2]
        res["bms_type"] = data[3]
        res["iot_type"] = data[4]
        res["iot_imei_number"] = data[5]
        res["sim_number"]= data[6]
        res["warrenty_start_date"] = data[7]
        res["warrenty_duration"] = data[8]
        res["assigned_owner"] = data[9]
        res["status"] = data[10]
        res["battery_cell_chemistry"] = data[11]
        res["battery_pack_nominal_voltage"] = data[12]
        res["battery_pack_nominal_charge_capacity"] = data[13]
        res["charging_status"] = data[14]
        res["vehicle_assign_id"] = data[15]
        res["is_assigned"] = data[16]
        my_data.append(res)

    cursor.close()
    return my_data