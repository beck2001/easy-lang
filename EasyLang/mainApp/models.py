from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, tg_id, name, surname, password, **extra_fields):
        if not tg_id:
            raise ValueError('The Tg ID must be set')
        if not name:
            raise ValueError('The name must be set')
        if not surname:
            raise ValueError('The surname must be set')
        if not password:
            raise ValueError('The password must be set')
        
        user = self.model(tg_id=tg_id, name=name, surname=surname, **extra_fields)
        
        
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, tg_id, name, surname, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(tg_id, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
        

    tg_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # default https://i.ytimg.com/vi/jYFk1O_t43A/maxresdefault.jpg
    img_url = models.CharField(max_length=500, default='https://i.ytimg.com/vi/jYFk1O_t43A/maxresdefault.jpg', blank=True, null=True)

    USERNAME_FIELD = 'tg_id'
    REQUIRED_FIELDS = ['name', 'surname']
    

    objects = UserManager()

    def __str__(self):
        return self.name + ' ' + self.surname
        
class Manager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.user.name + ' ' + self.user.surname
    
class Project(models.Model):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=500)
    deadline = models.DateField()
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    total_pages_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.name

class Translator(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.user.name + ' ' + self.user.surname

class Editor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.user.name + ' ' + self.user.surname
        

class Project_Translator(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    translator = models.ForeignKey(Translator, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.translator.user.name + ' ' + self.translator.user.surname + ' ' + self.project.name

class Project_Editor(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    editor = models.ForeignKey(Editor, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.editor.user.name + ' ' + self.editor.user.surname + ' ' + self.project.name

class Pages_per_day(models.Model):
    translator = models.ForeignKey(Translator, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    pages_count = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100000)])
    comment = models.CharField(max_length=500, blank=True, null=True)
    # make editable=True
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.translator.user.name + ' ' + self.translator.user.surname + ' ' + self.project.name + ' ' + str(self.pages_count)
    
    
class Approve(models.Model):
    # one to one
    pages_per_day = models.OneToOneField(Pages_per_day, on_delete=models.CASCADE, unique=True)
    editor = models.ForeignKey(Editor, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

class Disapprove(models.Model):
    pages_per_day = models.OneToOneField(Pages_per_day, on_delete=models.CASCADE, unique=True)
    editor = models.ForeignKey(Editor, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)