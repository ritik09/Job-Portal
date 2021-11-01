from django.db import models
from django.forms import ModelForm
from datetime import datetime
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password = None):

        if not email:
            raise ValueError('Users must have an email address')

        if not password:
            raise ValueError('Users must have an password')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.active = True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    username = models.CharField(max_length = 200, default = "", unique = False, blank = True)
    name = models.CharField(max_length = 200, default = "", null = False)
    email = models.EmailField(verbose_name = 'email address', max_length = 200, unique = True)
    confirm_password = models.CharField(max_length = 200, default = "", null = False)
    active = models.BooleanField(default = False)
    staff = models.BooleanField(default = False)
    admin = models.BooleanField(default = False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        return self.first_name

    def __str__(self):          
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

class Company(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, null = False)
    head_office_location = models.CharField(max_length = 200, default = "", blank = True)
    image = models.ImageField(upload_to = 'pics', default = "", blank = True)

    def __str__(self):
        return self.user.name

class Category(models.Model):
    category_name = models.CharField(max_length=200, default ="")

    def __str__(self):
        return self.category_name

class Location(models.Model):
    location_name = models.CharField(max_length = 200, default = "")
    
    def __str__(self):
        return self.location_name

class Jobs(models.Model):                    
    role = models.ForeignKey(Category, default = 1, on_delete = models.SET_DEFAULT, null = True)
    location = models.ForeignKey(Location, default = 1, on_delete = models.SET_DEFAULT, null = True)                                     
    job_description = models.TextField()                                                      
    date_published = models.DateTimeField("date published",default= datetime.now())                                           
    company = models.ForeignKey(Company,default=2,on_delete=models.SET_DEFAULT,null=True)    
    phone_regex = RegexValidator(regex=r"^[56789]\d{9}$")
    phone_number = models.CharField(validators=[phone_regex], max_length=10, blank=True, null=True)

    def __str__(self):          
        return str(self.role)