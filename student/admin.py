

from django.contrib import admin
from student.models import Student, WithdrawnStudent


admin.site.register([Student, WithdrawnStudent])
