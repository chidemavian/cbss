from django.contrib import admin
from lesson.models import *

admin.site.register([tbltopic, 
	tblcontents,
	tblir, 
	tblobjectives,
	tblteachersActivities,
	tblstudentActivities,
	tblevaluation])
