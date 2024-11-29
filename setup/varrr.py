from django.shortcuts import render_to_response, get_object_or_404
from django.http import  Http404, HttpResponseRedirect, HttpResponse
from django.core.serializers.json import json
from assessment.forms import *
from academics.models import *
from sysadmin.models import *
from setup.models import *
from assessment.getordinal import *
from assessment.utils import *
from assessment.bsheet import *
from utilities.views import *
from django.db.models import Max,Sum
import datetime
from datetime import date
import locale
locale.setlocale(locale.LC_ALL,'')
import xlwt

currse = currentsession.objects.get(id = 1)

def sublists(varuser,session,klass):
    data = subjectteacher.objects.filter(teachername = varuser,session=session,klass = klass)
    for j in data:
        j = j.subject
        s = {j:j}
        sdic.update(s)
    kb = sdic.values()
    return kb
