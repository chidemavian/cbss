from django.contrib import admin
from bill.models import *

admin.site.register([tblexpenses, tblbill,tbladditionalbill,postedbill,oldbill,billsession])
