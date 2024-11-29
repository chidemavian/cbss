__author__ = 'yusuf'

from django.contrib import admin
from academics.models import *


admin.site.register([StudentAcademicRecord, PsychomotorSkill, AffectiveSkill, SubjectScore])
