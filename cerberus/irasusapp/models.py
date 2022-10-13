# Create your models here.
from django.db import models
import datetime
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError

from user_management.models import Organisation,Role

class CrmUserManager(BaseUserManager):
    def create_user(self, email,username,contact, password=None, password_conformation=None):
        """
        Creates and saves a superuser with the given email,username,contact
        and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            contact=contact,
            password=password,
            password_conformation=password_conformation
        )

        user.set_password(password)
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
            username=username,
            contact=contact,
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

class Crmuser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=20,
        unique=True,
        primary_key=True
    )
    username = models.CharField(max_length=100, default='')
    contact = models.CharField(max_length=12, default='')
    password = models.CharField(max_length=100,default='', validators=[password_validator])
    password_conformation = models.CharField(max_length=100,default='',validators=[password_validator])
    last_login = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=datetime.datetime.now)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    orgs = models.ManyToManyField(Organisation)

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
    ('ion', 'ION'),
    ('electrifuel', 'ELECTRIFUEL'),
)

IOT_TYPE = (
    ('tarckmate', 'TRACKMATE'),
    ('electrifuel', 'ELECTRIFUEL'),
    ('aeidth', 'AEIDTH'),
)

STATUS = (
    ('in_swap_station', 'IN_SWAP_STATION'),
    ('in_vehicle', 'IN_VEHICLE'),
    ('idel', 'IDEL'),
    ('damaged','DAMAGED'),
)

class BatteryDetail(models.Model):
    model_name = models.CharField(max_length=100,default='', choices=MODEL_CHOICES, blank=True)
    battery_serial_num = models.CharField(max_length=100, primary_key=True, default='', unique=True)
    battery_type = models.CharField(max_length=100, default='', choices=BATTERY_TYPES)
    bms_type = models.CharField(max_length=100, default='', choices=BMS_TYPE)
    iot_type = models.CharField(max_length=100, default='', choices=IOT_TYPE)
    iot_imei_number = models.CharField(max_length=100)
    sim_number = models.CharField(max_length=12, default='', blank=True)
    warrenty_start_date = models.DateField(default='',blank=True)
    warrenty_duration = models.DateField(default='',blank=True)
    assigned_owner = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS, default='')
    battery_cell_chemistry = models.CharField(max_length=50, default='')
    battery_pack_nominal_voltage = models.CharField(max_length=50, default='')
    battery_pack_nominal_charge_capacity = models.CharField(max_length=50, default='')
    charging_status = models.CharField(max_length=50, default='')


    def __str__(self):
        return str(self.model_name)
