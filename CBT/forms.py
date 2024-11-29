from django import forms
from setup.models import *
from sysadmin.models import *
from student.models import *
from lesson.models import *
from CBT.models import *


def sess():
    return currentsession.objects.get(id = 1)

sess = currentsession.objects.get(id = 1)
# klassy = (('1 - 5', '1 - 5'), (('6', '6')))
klassy = (('YEAR 1', 'YEAR 1'),('YEAR 2', 'YEAR 2'),('YEAR 3', 'YEAR 3'),('YEAR 4', 'YEAR 4'), ('YEAR 5', 'YEAR 5'), ('YEAR 6', 'YEAR 6'))
exam = (('Welcome back', 'Welcome back'),('Mid Term Exam', 'Mid Term Exam'),('Ca2' , 'Ca2'),('End Term Exam', 'End Term Exam'))



class subform(forms.Form):
    session = forms.CharField(label='Session',max_length= 190,required=True,widget= forms.TextInput(attrs ={'size':'10','readonly':'readonly'}),initial=sess)
    klass = forms.ChoiceField(label='Class',choices = [(c.klass, c.klass) for c in Class.objects.all()])
    user = forms.CharField(label = "User",max_length = 20,required = True,widget = forms.TextInput())
    subject = forms.ChoiceField(label= 'Subject', choices = [(a.subject, a.subject) for a in Subject.objects.all()])


    def __init__(self, *args):
        super(subform, self).__init__(*args)
        self.fields['klass'].choices = [(c.klass, c.klass) for c in Class.objects.all()]
        self.fields['klass'].initial = Class.objects.all()
        self.fields['subject'].choices = [(a.subject, a.subject) for a in Subject.objects.all()]
        self.fields['subject'].initial = Subject.objects.all()
        self.fields['session'].widget.attrs['class'] = 'loginTxtbox'



class formactive(forms.Form):
    session = forms.CharField(label='Session',max_length= 190,required=True,widget= forms.TextInput(attrs ={'size':'10','readonly':'readonly'}),initial=sess)
    klass = forms.ChoiceField(label='Class',choices =klassy)
    # klass = forms.ChoiceField(label='Class',choices = [(c.klass, c.klass) for c in Class.objects.all()])
    subject = forms.ChoiceField(label= 'Subject', choices = [(a.subject, a.subject) for a in Subject.objects.filter(category= 'JS')])


    def __init__(self, *args):
        super(formactive, self).__init__(*args)
        self.fields['session'].widget.attrs['class'] = 'loginTxtbox'


class qstnform(forms.Form):
    session = forms.CharField(label='Session',max_length= 190,required=True,widget= forms.TextInput(attrs ={'size':'10','readonly':'readonly'}),initial=sess)
    klass = forms.ChoiceField(label='Class',choices = [(c.klass, c.klass) for c in Class.objects.all()])
    subject=forms.ChoiceField(label= 'Subject', choices = [(a.subject, a.subject) for a in Subject.objects.filter(category= 'JS')])
    term = forms.ChoiceField(label='Term',choices = [(c.term, c.term) for c in tblterm.objects.filter(status= 'ACTIVE')])
    exam_type = forms.ChoiceField(label='Exam Type',choices = [(a.exam_type, a.exam_type) for a in tblcbtexams.objects.filter(status='ACTIVE')])
    question = forms.CharField(label= 'Question', max_length= 99190)
    pix = forms.ImageField(required=False,widget=forms.FileInput(attrs={'size':'5'}),label='Student Picture')



    def __init__(self, *args):
        super(qstnform, self).__init__(*args)
        self.fields['session'].choices = [(c.session, c.session) for c in currentsession.objects.filter(id = 1)]
        self.fields['term'].choices = [(a.term, a.term) for a in tblterm.objects.filter(status = 'ACTIVE')]

