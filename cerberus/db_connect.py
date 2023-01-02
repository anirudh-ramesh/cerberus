import psycopg2 as db
import base64
import os
from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv())

def connect():
    conn=db.connect(host= os.getenv('HOST'),user=os.getenv('USER_NAME'),password=os.getenv('PASSWORD'),database=os.getenv('DATABASE_NAME'))
    return conn
    
# psql -h db -p 5432 -U myprojectuser -d postgres
#LIST ORGANISATION USER  
def sql_query(id):
    try:
        conn=connect()
        cursor=conn.cursor()
        sql= f"SELECT email FROM irasusapp_crmuser WHERE NOT EXISTS (SELECT email,serial_number FROM user_management_organisation_user_role_one WHERE user_management_organisation_user_role_one.serial_number = '{id}' AND irasusapp_crmuser.email = user_management_organisation_user_role_one.email);"
        cursor.execute(sql)
        myresult = cursor.fetchall()
        new_data=[]
        for data in myresult:
            new_data.append(data[0])
        cursor.close()    
        return new_data
    except Exception as e:
        print(e)

#INSERT USER INTO ORGANISATION
def inset_into_db(data,id,role,select):
    try:
        conn=connect()
        cursor=conn.cursor()
        query = 'INSERT INTO user_management_organisation_user_role_one(serial_number,email,id,user_status) \
        VALUES(%s,%s,%s,%s)'                                                         
        my_data = []
        for row in data:
            my_data.append((id,row,str(role),select))
        cursor.executemany(query, my_data)
        conn.commit()
        cursor.close()
        return
    except Exception as e:
        print(e)

#LIST ORGANISATION INFO
def getOrgUserInfo(id):
    try:
        conn=connect()
        cursor=conn.cursor()
        sql = f"SELECT \
        irasusapp_crmuser.email,irasusapp_crmuser.username,user_management_organisation_user_role_one.id \
        FROM irasusapp_crmuser \
        LEFT JOIN user_management_organisation_user_role_one ON irasusapp_crmuser.email = user_management_organisation_user_role_one.email \
        WHERE user_management_organisation_user_role_one.serial_number='{id}'AND user_management_organisation_user_role_one.user_status=True"
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
    except Exception as e:
        return []

def getOrgInfobyEmail(email):
    try:
        conn=connect()
        cursor=conn.cursor()
        sql = f"select * from user_management_organisation_user_role_one where email='{email}'"
        cursor.execute(sql)
        myresult = cursor.fetchall()
        my_data = []
        for row in myresult:
            
            my_data.append(row[1])
        cursor.close()
        return my_data
    except Exception as e:
        print(e)

#ADD ORGANISATION PROFILE DATA
def orgProfileAddData(id,orgprofile_id):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = 'INSERT INTO user_management_organisation_organisation_profile(organisation_id,organisationprofile_id) \
        VALUES(%s,%s)'
        my_data = (id,orgprofile_id)
        cursor.execute(sql, my_data)
        conn.commit()
        cursor.close()
        return
    except Exception as e:
        print(e)

#LIST ORGANISATION PROFILE
def getOrgProfiles(id):
    try:
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
            res['id']= str(row[0])
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
            res['serial_number'] = row[21]
            new_data.append(res)           
        cursor.close()
        return new_data
    except Exception as e:
        return []

#LIST ORGANISATION ROLE
def getOrgRoles(id):
    try:
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
    except Exception as e:
        return []

#UPDATE ORGANISATION USER
def orgUserUpdateData(role,serial_number,email):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = f"UPDATE user_management_organisation_user_role_one set id='{role}' WHERE serial_number ='{serial_number}' AND email='{email}';"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        return
    except Exception as e:
        print(e)

#LIST ORGANISATION PERMISSION
def organisationmultiplePermission(id):
    try:
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
    except Exception as e:
        return []

#INSERT ORGANISATION PERMISSION
def insertIntoOrgnisationPermission(permission_name,role_name,id):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = 'INSERT INTO user_management_organisationpermission(permission_name,role_name,role_id) \
        VALUES(%s,%s,%s)'
        my_data = (permission_name,role_name,id)
        cursor.execute(sql, my_data)
        conn.commit()
        cursor.close()
        return
    except Exception as e:
        print(e)

#Update Organisation Permission
def updateOrgAssignPermission(permission_name,role_name,id):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = f"UPDATE user_management_organisationpermission set permission_name='{permission_name}', role_name='{role_name}' WHERE id ='{id}';"
        my_data = (permission_name,role_name,id)
        cursor.execute(sql,my_data)
        conn.commit()
        cursor.close()
        return
    except Exception as e:
        print(e)

#REMOVE USER FROM ORGANISATION
def removeUserFromOrg(select,serial_number,email):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = f"UPDATE user_management_organisation_user_role_one set user_status='{select}' WHERE serial_number ='{serial_number}' AND email='{email}';"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        return
    except Exception as e:
        print(e)

#ASSIGNED BATTERY DATA
def listAssignedBatteryVehicle(id):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = f"SELECT \
        irasusapp_batterydetail.model_name, irasusapp_batterydetail.battery_serial_num, irasusapp_batterydetail.battery_type, \
        irasusapp_batterydetail.bms_type,irasusapp_batterydetail.iot_type,irasusapp_batterydetail.iot_imei_number_id,irasusapp_batterydetail.sim_number,\
        irasusapp_batterydetail.warrenty_start_date,irasusapp_batterydetail.warrenty_duration, irasusapp_batterydetail.assigned_owner,irasusapp_batterydetail.status,\
        irasusapp_batterydetail.battery_cell_chemistry,irasusapp_batterydetail.battery_pack_nominal_voltage,\
        irasusapp_batterydetail.battery_pack_capacity, irasusapp_batterydetail.charging_status, irasusapp_batterydetail.vehicle_assign_id,irasusapp_batterydetail.is_assigned\
        FROM irasusapp_batterydetail \
        RIGHT JOIN irasusapp_vehicle ON irasusapp_vehicle.chasis_number = irasusapp_batterydetail.vehicle_assign_id \
        WHERE irasusapp_vehicle.chasis_number='{id}'"
        cursor.execute(sql)
        myresult = cursor.fetchall()
        my_data = []
        for data in myresult:
            res= {}
            if(data[0] == None):
                break
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
            res["battery_pack_capacity"] = data[13]
            res["charging_status"] = data[14]
            res["vehicle_assign_id"] = data[15]
            res["is_assigned"] = data[16]
            my_data.append(res)

        cursor.close()
        return my_data
    except Exception as e:
        return []


#ASSIGNED-VECHICLE-TO-ORGANISATION
def assignedVehicleToOrganisation(id, vehicle_id):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = 'INSERT INTO user_management_organisation_vehicle_assign(organisation_id,vehicle_id) \
        VALUES(%s,%s)'
        my_data = (id,vehicle_id)
        cursor.execute(sql, my_data)
        conn.commit()
        cursor.close()
        return
    except Exception as e:
        return []


#ORGANISATION-ASSIGNED-VEHICLE
def getOrgAssignedVehicle(id):
    try:
        conn=connect()
        cursor=conn.cursor()
        sql = f"SELECT \
        * \
        FROM irasusapp_vehicle \
        LEFT JOIN user_management_organisation_vehicle_assign ON irasusapp_vehicle.chasis_number = user_management_organisation_vehicle_assign.vehicle_id \
        WHERE user_management_organisation_vehicle_assign.organisation_id='{id}'"
        cursor.execute(sql)
        myresult = cursor.fetchall()
        new_data = []
        for data in myresult:
            res={}
            res["vehicle_model_name"] = str(data[0])
            res["chasis_number"] = data[1]
            res["configuration"] = data[2]
            res["vehicle_choice"] = data[3]
            # res["vehicle_iot_imei_number"] = data[4]
            # res["vehicle_sim_number"] = data[4]
            res["vehicle_warrenty_start_date"]= data[4]
            res["vehicle_warrenty_end_date"] = data[5]
            res["assigned_owner"] = data[6]
            res["insurance_start_date"] = data[7]
            res["insurance_end_date"] = data[8]
            res["organisation_id"] = data[12]
            new_data.append(res)
        cursor.close()
        return new_data
    except Exception as e:
        return []

#REMOVE ASSIGNED-VEHICLE FROM ORGANISATION
def removeAssignedVehiclefromOrganisation(org_id,vehicle_id):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = f"DELETE FROM user_management_organisation_vehicle_assign WHERE organisation_id='{org_id}' AND vehicle_id='{vehicle_id}';"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        return
    except Exception as e:
        print(e)

#LIST ASSIGNED-VEHICLE
def listAssignedVehicleToUser(id):
    try:
        conn = connect()
        cursor = conn.cursor()
        sql = f"SELECT \
            irasusapp_crmuser.email,irasusapp_crmuser.username,irasusapp_crmuser.is_active,irasusapp_vehicle.vehicle_model_name, irasusapp_vehicle.chasis_number, irasusapp_vehicle.configuration, \
            irasusapp_vehicle.vehicle_choice,irasusapp_vehicle.vehicle_warrenty_start_date,irasusapp_vehicle.vehicle_warrenty_end_date,\
            irasusapp_vehicle.assigned_owner, irasusapp_vehicle.insurance_start_date,irasusapp_vehicle.insurance_end_date,irasusapp_vehicle.vehicle_selected \
            FROM irasusapp_crmuser \
            LEFT JOIN irasusapp_vehicle ON irasusapp_vehicle.assigned_to_id = irasusapp_crmuser.email \
            WHERE irasusapp_crmuser.email='{id}'"

        cursor.execute(sql)
        myresult = cursor.fetchall()
        vehicle_data = []
        for data in myresult:
            res={}
            res["email"] = str(data[0])
            res["username"] = data[1]
            res["is_active"] = data[2]
            res["vehicle_model_name"]=data[3]
            res["chasis_number"]=data[4]
            res["configuration"]=data[5]
            res["vehicle_choice"]=data[6]
            # res["vehicle_iot_imei_number"]=data[7]
            # res["vehicle_sim_number"]=data[7]
            res["vehicle_warrenty_start_date"]=data[7]
            res["vehicle_warrenty_end_date"]=data[8]
            res["assigned_owner"]=data[9]
            res["insurance_start_date"]=data[10]
            res["insurance_end_date"]=data[11]
            res["vehicle_selected"]=data[12]
            
            vehicle_data.append(res)

            cursor.close()
        return vehicle_data
    except Exception as e:
        return []

#REMOVE VECHILE FROM USER
def removeUserVehicle(select,chasis_number):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = f"UPDATE irasusapp_vehicle set assigned_to_id=NULL,vehicle_selected={select} WHERE chasis_number='{chasis_number}';"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
    except Exception as e:
        print(e)


#CONVERY BINARY DATA TO UTF-8 TO SHOW IMAGES
def images_display(check):
    try:
        sql=""
        if(check== True):
            sql=f"SELECT email,username,user_type,is_active,adhar_proof,pancard_proof,license_proof FROM irasusapp_crmuser WHERE user_type='Driver'"
        else:
            sql=f"SELECT email,username,user_type,is_active,adhar_proof,pancard_proof,license_proof FROM irasusapp_crmuser WHERE user_type='Driver' AND created_id='{str(check)}'"
        conn=connect()
        cursor = conn.cursor()
        sql = "SELECT email,username,user_type,is_active,adhar_proof,pancard_proof,license_proof,vehicle_assigned_id, assigned_operator FROM irasusapp_crmuser WHERE user_type='Driver';"
        cursor.execute(sql)
        results = cursor.fetchall()
        one_row = []
        for value in results:
        
            res={}
            res['email'] = value[0]
            res['username'] = value[1]
            res['user_type'] = value[2]
            res['is_active'] = value[3]
            res['adhar_proof'] = base64.b64encode(value[4]).decode("utf-8")
            res['pan_proof'] = base64.b64encode(value[5]).decode("utf-8")
            res['driving_license'] = base64.b64encode(value[6]).decode("utf-8")
            res['vehicle_assigned_id'] = value[7]
            res['assigned_operator'] = value[8]
            one_row.append(res)
        return one_row
    except Exception as e:
        print("-=-=-=",e)
        return []

def iotDevice(iotList):
    try:
        conn = connect()
        cursor = conn.cursor()
        sql = f"SELECT irasusapp_batterydetail.model_name,irasusapp_batterydetail.battery_serial_num, irasusapp_batterydetail.iot_imei_number_id FROM irasusapp_batterydetail \
            LEFT JOIN irasusapp_iotdevices ON irasusapp_iotdevices.imei_number = irasusapp_batterydetail.iot_imei_number_id \
        "
        cursor.execute(sql)
        myresult = cursor.fetchall()
        new_data=[]
        for iot in iotList:
            res={}
            continueForLoop=False
            for data in myresult:
                if(data[2] == iot["imei_number"]):
                    res["model_name"]=data[0]
                    res["battery_serial_num"]=data[1]
                    res["iot_imei_number_id"]=iot["imei_number"]
                    res["hardware_version"]=iot["hardware_version"]
                    res["firmware_version"]=iot["firmware_version"]
                    res['status'] = iot['status']
                    res["assign"] =True
                    new_data.append(res)
                    continueForLoop=True
                    continue
            if(continueForLoop):
                continue
            res["iot_imei_number_id"]=iot["imei_number"]
            res["hardware_version"]=iot["hardware_version"]
            res["firmware_version"]=iot["firmware_version"]
            res['status'] = iot['status']
            res["assign"] = False
            new_data.append(res)
        return new_data
    except Exception as e:
        return []

def insertDataintoGeofenceVehicle(vehicle_id,geofence_id):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = 'INSERT INTO irasusapp_vehicle_geofence(vehicle_id,geofence_id) \
        VALUES(%s,%s)'
        my_data = (vehicle_id,geofence_id)
        cursor.execute(sql, my_data)
        conn.commit()
        cursor.close()
        return
    except Exception as e:
        print(e)

def listGeofenceVehicle(id):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = f"SELECT \
        irasusapp_geofence.geoname, irasusapp_geofence.description, irasusapp_geofence.pos_address, irasusapp_vehicle_geofence.geofence_id,irasusapp_vehicle_geofence.vehicle_id,irasusapp_vehicle_geofence.id  \
        FROM irasusapp_geofence \
        LEFT JOIN irasusapp_vehicle_geofence ON irasusapp_geofence.id = irasusapp_vehicle_geofence.geofence_id \
        WHERE irasusapp_vehicle_geofence.geofence_id='{id}'"
        cursor.execute(sql)
        myresult = cursor.fetchall()
        new_data = []
        for data in myresult:
            res={}
            res['geoname'] = data[0]
            res['description'] = data[1]
            res['pos_address'] = data[2]
            res['geofence_id'] = data[3]
            res['vehicle_id'] = data[4]
            res['id'] = data[5]
            new_data.append(res)
        return new_data
    except Exception as e:
        return []

def removeUserVehicle(id):
    try:
        conn=connect()
        cursor = conn.cursor()
        sql = f"DELETE FROM irasusapp_vehicle_geofence WHERE id={id};"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
    except Exception as e:
        print(e)