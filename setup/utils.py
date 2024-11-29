
import os
from xlwt import Workbook, easyxf
from xhtml2pdf import pisa
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils.html import escape
from student.models import *

import datetime
from datetime import date
import random


try:
    import cStringIO as StringIO
except:
    import StringIO

def generate_admissionno(session):
    currr = session.split('/')[0]
    dd = []

    stu = Student.objects.filter(admitted_session=session)
    if stu.count() == 0 :
        stdno = 0
    else:
        for j in stu:
            sno = j.admissionno
            curr = sno.split('/')[1]
            currb= int(curr)
            dd.append(currb)
        dd.sort(reverse= True)
        stdno = dd[0]
    stnno = int(stdno)
    stnno1 = stnno + 1
    tday = datetime.date.today()
    ty = tday.year
    typ = str(ty)
    tyy = typ[2:]

    k = random.randint(0,9)
    y = random.randint(0,9)
    x = random.randint(0,9)
    z = random.randint(0,9)
    a = random.randint(0,9)

    pin =  str(k) + str(y) + str(x) + str(z)

    g= stu.filter(gone=0)

    if g==0:
        data=1
    else:
        data=g.count()
        data +=  1

    reg = 'CBSS/%s/%.4d/%s'%(currr[2:], data,pin) 
    return reg