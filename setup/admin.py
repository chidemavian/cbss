from django.contrib import admin
from setup.models import  *

admin.site.register([Subject, Class, Role, Department, Arm, LGA,School,subclass,gradingsys,appused])
