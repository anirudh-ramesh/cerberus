# Create your models here.
from django.contrib.gis.db import models
import datetime
import base64

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError

from user_management.models import Organisation

class CrmUserManager(BaseUserManager):
    def create_user(self, email,password=None, password_conformation=None):
        """
        Creates and saves a superuser with the given email,username,contact
        and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            password=password,
            password_conformation=password_conformation
        )

        # user.check_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,username,contact, password=None, password_conformation=None):
        """
        Creates and saves a superuser with the given email,username,contact
        and password.
        """
        user = self.create_user(
            email,
            password=password,
            password_conformation=password_conformation
            
        )
        # user.is_admin = True
        user.save(using=self._db)
        return user


def password_validator(value):
    if len(value) < 8:
        raise ValidationError(
            str('is too short (minimum 8 characters)'),
            code='invalid'
        )

USER_TYPE = (
    ('Admin', 'Admin'),
    ('Driver', 'Driver'), 
    ('User', 'User')
)

#USER-TABLE
class Crmuser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        unique=True,
        primary_key=True
    )
    username = models.CharField(max_length=100, default='')
    contact = models.CharField(max_length=12, default='')
    password = models.CharField(max_length=100,default='', validators=[password_validator])
    password_conformation = models.CharField(max_length=100,default='',validators=[password_validator])
    last_login = models.DateTimeField(verbose_name="last login",auto_now=True)
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=datetime.datetime.now)
    user_type = models.CharField(max_length=100, default='', choices=USER_TYPE)
    adhar_proof = models.BinaryField(null=True, blank=True)
    pancard_proof = models.BinaryField(null=True,blank=True)
    license_proof = models.BinaryField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    orgs = models.ManyToManyField(Organisation)
    vehicle_assigned = models.ForeignKey("Vehicle",default=None,on_delete=models.CASCADE, null=True, blank=True)


    objects = CrmUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'contact','password', 'password_conformation']

    class Meta:
        permissions = (
            ("search_users", "Can search"),
            ("add", "Can add user"),
            ("update", "Can update user"),
            ("delete", "Can delete user"),
            ("assign role", "Can Assign role"))

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    @staticmethod
    def get_user_by_email(email):
        try:
            return Crmuser.objects.get(email=email)
        except:
            return False
    

CHOICE_TYPE = (
    ('1', 'Entered'), 
    ('2', 'Exit')
)

# GEOFENCE-TABLE
class Geofence(models.Model):
    geofence = models.PolygonField(srid=4326, null=True, blank=True)
    geotype = models.CharField(blank=True, max_length=100,choices=CHOICE_TYPE, null=True)
    location = models.PointField(srid=4326, null=True, blank=True)
    description = models.CharField(default='', max_length=5000)
    enter_latitude = models.CharField(default='', max_length=5000, null=True, blank=True)
    enter_longitude = models.CharField(default='', max_length=5000, null=True, blank=True)
    pos_address = models.CharField(default='', max_length=5000)
    geoname = models.CharField(default='', max_length=225)

    def __str__(self):
        return self.geoname

CONFIGURATION = (
    ('48V','48V'),
    ('60V','60V'),
    ('72V','72V'),
)

VEHICLE = (
    ('2W-L', '2W-L'),
    ('2W-H','2W-H'),
    ('3W-Erickshaw','3W-Erickshaw'),
    ('3W-Loader','3W-Loader'),
)

#VEHICLE-TABLE
class Vehicle(models.Model):
    vehicle_model_name = models.CharField(max_length=225, default='')
    chasis_number = models.CharField(max_length=225, default='',primary_key=True)
    configuration = models.CharField(max_length=20, default='', choices=CONFIGURATION)
    vehicle_choice = models.CharField(max_length=225, default='', choices=VEHICLE)
    vehicle_warrenty_start_date = models.DateField(default='',blank=True,null=True)
    vehicle_warrenty_end_date = models.DateField(default='',blank=True, null=True)
    assigned_owner = models.CharField(max_length=225, default='')
    insurance_start_date = models.DateField(default='',blank=True,null=True)
    insurance_end_date = models.DateField(default='',blank=True, null=True)
    vehicle_selected = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(Crmuser,default=None,on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateField(blank=True,null=True)
    vehicle_status = models.CharField(max_length=225,default='', blank=True, null=True)
    # geofence = models.ManyToManyField(Geofence)

    def __str__(self):
        return str(self.vehicle_model_name)

class IotDevices(models.Model):
    imei_number = models.CharField(max_length=225, blank=True, primary_key=True)
    hardware_version = models.CharField(max_length=225, blank=True, null=True)
    firmware_version = models.CharField(max_length=225, blank=True, null=True)
    status = models.CharField(max_length=225,default='', blank=True, null=True)


    def __str__(self):
        return str(self.imei_number)

MODEL_CHOICES = (
    ('igtblu','IGTBLU'),
    ('igtred','IGTRED'),
    ('igtred+','IGTRED+'),
)

BATTERY_TYPES = (
    ('24','24'),
    ('48','48'),
    ('60','60'),
    ('72','72'),
)

BMS_TYPE = (
    ('ION', 'ION'),
    ('ELECTRIFUEL', 'ELECTRIFUEL'),
)

IOT_TYPE = (
    ('trackmate', 'TRACKMATE'),
    ('electrifuel', 'ELECTRIFUEL'),
    ('aeidth-IGT', 'AEIDTH-IGT'),
)

STATUS = (
    ('IN_SWAP_STATION', 'IN_SWAP_STATION'),
    ('IN_VEHICLE', 'IN_VEHICLE'),
    ('IDEL', 'IDEL'),
    ('DAMAGED','DAMAGED'),
)

CHARGING_STATUS = (
    ('FULL CHARGE', 'FULL CHARGE'),
    ('HALF CHARGE', 'HALF CHARGE'),
    ('INITIAL', 'INITIAL'),
    ('DAMAGED','DAMAGED'),
)
#BATTERY-TABLE
class BatteryDetail(models.Model):
    model_name = models.CharField(max_length=225,default='', choices=MODEL_CHOICES, blank=True)
    battery_serial_num = models.CharField(max_length=225, primary_key=True, default='', unique=True)
    battery_type = models.CharField(max_length=225, default='', choices=BATTERY_TYPES)
    bms_type = models.CharField(max_length=225, default='', choices=BMS_TYPE)
    iot_type = models.CharField(max_length=225, default='', choices=IOT_TYPE)
    iot_imei_number = models.ForeignKey(IotDevices, on_delete=models.CASCADE, null=True, blank=True)
    sim_number = models.CharField(max_length=225, default='', blank=True)
    warrenty_start_date = models.DateField(default='',blank=True,null=True)
    warrenty_duration = models.DateField(default='',blank=True, null=True)
    assigned_owner = models.CharField(max_length=225)
    status = models.CharField(max_length=225, choices=STATUS, default='')
    battery_cell_chemistry = models.CharField(max_length=225, default='')
    battery_pack_nominal_voltage = models.CharField(max_length=225, default='')
    battery_pack_capacity = models.CharField(max_length=225, default='')
    charging_status = models.CharField(max_length=225, default='', choices=CHARGING_STATUS,blank=True)
    is_assigned = models.BooleanField(default=False)
    vehicle_assign = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.model_name)

class FleetOperator(models.Model):
    username = models.CharField(max_length=225, blank=True)
    email = models.CharField(max_length=225, blank=False)
    is_admin = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    fleetId = models.CharField(max_length=225, blank=False)
    permission = models.CharField(max_length=4000, blank=True,null=True)

    def __str__(self):
        return str(self.model_name)



class FleetOwner(models.Model):
    username = models.CharField(max_length=225, blank=False)
    email = models.CharField(max_length=225, blank=False)
    is_admin = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    permission = models.CharField(max_length=4000, blank=True,null=True)
    
    def __str__(self):
        return str(self.model_name)

