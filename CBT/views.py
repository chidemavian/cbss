# Create your views here.
from django.shortcuts import render_to_response
from django.http import  Http404, HttpResponseRedirect, HttpResponse
from CBT.forms import *
from setup.models import *
from sysadmin.models import *
from student.models import *
from CBT.models import *
from django.core.serializers.json import json
import random
from django.db.models import Max,Sum
from academics.models import *

currse = currentsession.objects.get(id = 1)
term =tblterm.objects.get(status="ACTIVE")
term=term.term
school=School.objects.get(id =1)
ex=tblcbtexams.objects.get(status='ACTIVE')


switch=0


def chroose(request):
    if  "userid" in request.session:
        varuser=request.session['userid']
        return render_to_response('CBT/success.html',{'varuser':varuser})
    else:
        return HttpResponseRedirect('/login/')

def assignment(request):
	if "userid" in request.session:
		varuser=request.session['userid']
		user = tblcbtuser.objects.all()
		if request.method=='POST':
			form= subform(request.POST)
			if form.is_valid():
				session=form.cleaned_data['session']
				klass=form.cleaned_data['klass']
				subject=form.cleaned_data['subject']
				user=form.cleaned_data['user']
				user=user.upper()
				if tblcbtuser.objects.filter(session=session,klass=klass,user=user,subject=subject).count()==0:
					tblcbtuser(session=session,klass=	klass,subject=subject,user=	user).save()
			        return HttpResponseRedirect('/cbt/set_user/subject/')

			else:
				return render_to_response('CBT/entub.html',{'varuser':varuser,'form':form,'user':user})

		else:
			form = subform()

		return render_to_response('CBT/entub.html',{'varuser':varuser,'form':form,'user':user})
	else:
		return HttpResponseRedirect('/login')


def cbtstat(request):
	if "userid" in request.session:
		varuser= request.session['userid']
		sub= Subject.objects.filter(category = 'PRY')
		if request.method=='POST':
			form=formactive(request.POST)
			if form.is_valid():
				session=form.cleaned_data['session']
				klass=form.cleaned_data['klass']
				subject=form.cleaned_data['subject']
		else:
			form = formactive()

		return render_to_response('CBT/active.html',{'varuser':varuser,'form':form,'sub':sub})
	else:
		return HttpResponseRedirect('/login')

def qstn(request):
    if 'userid' in request.session:
        varuser = request.session['userid']
        if request.method=='POST':
            form = qstnform(request.POST, request.FILES)
            if form.is_valid():
                session=form.cleaned_data['session']
                klass=form.cleaned_data['klass']
                term=form.cleaned_data['term']
                subject=form.cleaned_data['subject']
                exam_type=form.cleaned_data['exam_type']
                question=form.cleaned_data['question']
                rfile=form.cleaned_data['pix']

                if rfile is None:
                    pix = '/ax/image'
                else:
                    pix = request.FILES['pix']

                data = tblquestion(instruction_to=  'instruction',session=session,
                    klass=klass,section='A',term=term,subject=subject,
                    exam_type=  exam_type,qstn =question,
                    topic='topic', image=pix).save()
                err= 'question saved successfully'
            else:
                err = 'spaces left not filled'
        else:
            form = qstnform()
            err=''
        return render_to_response('CBT/qstn.html',{'varuse':varuser,'form':form,'qstn':qstn,'err':err})
    else:
        return HttpResponseRedirect('/login')


def editcbtqst(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                state=acccode
                getdetails=[]
                details = tblquestion.objects.get(id = state)

                try:

                    options=tbloptions.objects.get(qstn=details)
                except:

                    options=''

                try:
                    answer= tblans.objects.get(qstn=details)

                except:
                     answer=''
                dicdetails={'options':options,'question':details,'answer':answer}
                return render_to_response('CBT/viewimage.html',{'getdetails':dicdetails,'state':options})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            getdetails = tblcontents.objects.filter(topic=id)
            return render_to_response('lesson/entersub.html',{'gdata':getdetails})
    else:
        return HttpResponseRedirect('/login/')






def getcbtqst(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                state=acccode
                session,term,klass,subject,exam_type= acccode.split(':')
                myqst=[]
                myqst=tblquestion.objects.filter(session=session,
                	term=term,
                	klass=klass,
                	subject=subject,
                	exam_type=exam_type).order_by('klass')

                # for q in myqst:
                #     opt=tbloptions.objects.filter(qstn=q).count()
                #     data={'question':q,'count':opt}
                #     myqst.append(data)

                return render_to_response('CBT/myqst.html',{'myqst':myqst,
                'term':term,'subject':subject,'exam':exam_type,'klass':klass,'session':session})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')



def optajax(request):
        if  "userid" in request.session:
            if request.is_ajax():
                if request.method == 'POST':
                    varuser = request.session['userid']
                    varerr =""
                    post = request.POST.copy()
                    acccode = post['userid']
                    state=acccode

                    getdetails=[]


                    details = tblquestion.objects.get(id = state)

                    try:

                        options=tbloptions.objects.get(qstn=details)

                        # answer= tblans.objects.get(qstn=details)

                    except:

                        options=''

                    try:
                        answer= tblans.objects.get(qstn=details)

                    except:
                         answer=''

                    dicdetails={'options':options,'question':details,'answer':answer}

                    return render_to_response('CBT/enteropt.html',{'getdetails':dicdetails,'state':options})
                    # return render_to_response('CBT/enteropt.html',{'getdetails':getdetails,'state':options})
                else:
                    gdata = ""
                    return render_to_response('index.html',{'gdata':gdata})
            else:

                getdetails = tblcontents.objects.filter(topic=id)
                return render_to_response('lesson/entersub.html',{'gdata':getdetails})
        else:
            return HttpResponseRedirect('/login/')




def doentry(request):
        if  "userid" in request.session:
            if request.is_ajax():
                if request.method == 'POST':
                    varuser = request.session['userid']
                    varerr =""
                    post = request.POST.copy()
                    acccode = post['userid']
                    state=acccode

                    getdetails=[]


                    details = tblquestion.objects.get(id = state)

                    try:

                        options=tbloptions.objects.get(qstn=details)

                        # answer= tblans.objects.get(qstn=details)

                    except:

                        options=''

                    try:
                        answer= tblans.objects.get(qstn=details)

                    except:
                         answer=''


                    dicdetails={'options':options,'question':details,'answer':answer}


                    # getdetails=getdetails.append(dicdetails)


                    return render_to_response('CBT/edditall.html',{'getdetails':dicdetails,'state':options})

                else:
                    gdata = ""
                    return render_to_response('index.html',{'gdata':gdata})
            else:

                getdetails = tblcontents.objects.filter(topic=id)
                return render_to_response('lesson/entersub.html',{'gdata':getdetails})
        else:
            return HttpResponseRedirect('/login/')



def myoptions(request,vid):
    if "userid" in request.session:
        varuser=request.session['userid']
        if 'option' in request.POST:
            if request.method=='POST':


                a=request.POST['optiona']
                b=request.POST['optionb']
                c=request.POST['optionc']
                d=request.POST['optiond']

                if a=='' or b=='' or c=='' or d=='':
                    g='na me be this?'

                    return HttpResponseRedirect('/cbt/options/')

                qst=tblquestion.objects.get(id=vid)

                tbloptions(a=a,b=b,c=c,d=d,e='non of the above',qstn=qst).save()

                option = request.POST['option']

                if option=='A':
                    tblans(ans =a,option=option,qstn=qst).save()
                elif option=='B':
                    tblans(ans =b,option=option,qstn=qst).save()
                elif option=='C':
                    tblans(ans =c,option=option,qstn=qst).save()
                elif option=='D':
                    tblans(ans =d,option=option,qstn=qst).save()


                g= 'my name is mathew'




                return HttpResponseRedirect('/cbt/options/')#

            else:
                return HttpResponseRedirect('/login/')
        else:
            f = 'my name is black'
            return HttpResponseRedirect('/cbt/options/')
    else:
        return HttpResponseRedirect('/login/')




def editquestion(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                # state=acccode
                session,term,klass,subject,exam_type= acccode.split(':')
                sublist=[]
                myqst=tblquestion.objects.filter(session=session,
                    term=term,
                    klass=klass,
                    subject=subject,
                    exam_type=exam_type).order_by('klass')
                if myqst.count()==0:
                    varerr = 'NO QUESTIONS ENTERED'
                    return render_to_response('CBT/myopt.html',{'varerr':varerr})
                else:
                    for j in myqst:
                        k = tbloptions.objects.filter(qstn=j)
                        intr= {'question':j,'options':k}
                        sublist.append(intr)
                return render_to_response('CBT/myedit.html',{'sublist':sublist})
        else:
            return HttpResponseRedirect('/login/')
    else:
        return HttpResponseRedirect('/login/')




def getcbtopt(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                # state=acccode
                session,term,klass,subject,exam_type= acccode.split(':')
                sublist=[]
                myqst=tblquestion.objects.filter(session=session,
                	term=term,
                	klass=klass,
                	subject=subject,
                	exam_type=exam_type).order_by('klass')
                if myqst.count()==0:
                	varerr = 'NO QUESTIONS ENTERED'
                	return render_to_response('CBT/myopt.html',{'varerr':varerr})
                else:
                    for j in myqst:
                        k = tbloptions.objects.filter(qstn=j)
                        intr= {'question':j,'options':k}
                        sublist.append(intr)
                return render_to_response('CBT/myopt.html',{'sublist':sublist})
        else:
            return HttpResponseRedirect('/login/')
    else:
        return HttpResponseRedirect('/login/')





def options(request):
    if "userid" in request.session:
        varuser=request.session['userid']
        form= qstnform
        qst = tblquestion.objects.all()
        return render_to_response('CBT/options.html',{'varuser':varuser,'form':form,'qst':qst})
    else:
        return HttpResponseRedirect('/login')


def editq(request):
    if "userid" in request.session:
        varuser=request.session['userid']
        form= qstnform
        qst = tblquestion.objects.all()
        return render_to_response('CBT/edit.html',{'varuser':varuser,'form':form,'qst':qst})
    else:
        return HttpResponseRedirect('/login')



def theory(request):
    if "userid" in request.session:
        varuser=request.session['userid']
        if request.method=='POST':
            form=qstnform(request.POST)
            if form_is.is_valid():
                session=form.cleaned_data['session']
                term=form.cleaned_data['term']
                klass=form.cleaned_data['klass']
                exam_type=form.cleaned_data['exam_type']
                subject=form.cleaned_data['subject']
                return HttpResponseRedirect('/cbt/enter/theory/')
        else:
            form = qstnform()
        return render_to_response('CBT/theory.html',{'varuser':varuser,'form':form})

    else:
        return HttpResponseRedirect('/login/')


def clear(request):
    if "userid" in request.session:
        if request.method=='POST':
            varuser=request.session['userid']
            student=Student.objects.get(admitted_session=currse, fullname=varuser,gone=False)
            session=student.admitted_session
            cbttrans.objects.filter(student=student,
                term=term,session=session,exam_type=ex.exam_type,subject='BASIC SCIENCE').delete()

            cbtcurrentquestion.objects.filter(student=student,
                session=currse,term=term,exam_type=ex.exam_type,subject='BASIC SCIENCE').delete()
            cbtold.objects.filter(student=student,session=currse,term=term,
                exam_type=ex.exam_type,subject='BASIC SCIENCE').delete()

            return HttpResponseRedirect('/welcome/')
        else:
            return HttpResponseRedirect('/login/')
    else:
        return HttpResponseRedirect('/login/')




def pupilcbt(request):
    msg = 'CBT MODULE STARTS NEXT TERM'
    return render_to_response('CBT/selectloan.html',{'msg':msg})

def pupilcbtc(request):
    if "userid" in request.session:
        if request.method=='POST':
            varuser=request.session['userid']
            student=Student.objects.get(admitted_session=currse, fullname=varuser,gone=False)

            sub =0
            sub=int(tblcbtsubject.objects.filter(klass=student.admitted_class,
                term=term,
                session=student.admitted_session,
                status='ACTIVE').count())

            subject=tblcbtsubject.objects.get(klass=student.admitted_class,
                term=term,
                session=student.admitted_session,
                status='ACTIVE')

            subject=subject.subject

            total_questions=tblquestion.objects.filter(session=currse,term=term,
                klass=student.admitted_class,
                section='A',exam_type=ex.exam_type,
                subject=subject).count()


            fq=cbtcurrentquestion.objects.filter(student=student,
                session=currse,
                term=term,
                subject=subject,
                exam_type=ex.exam_type).count()



            if fq==0:

                img='image'


                if sub == 1:   #meaning nomber of active subject for that class
                    sub=tblcbtsubject.objects.get(klass=student.admitted_class, session=student.admitted_session, status='ACTIVE')
                    subject=sub.subject

                    trans=cbttrans.objects.filter(session=currse,
                        exam_type=ex.exam_type,
                        student=student, #or student.id
                        subject=subject,
                        term=term)


                    transid=[]
                    for k in trans:
                        fb= k.qstcode.split('-')[0]
                        fb=int(fb)
                        transid.append(fb)

                    qstns=tblquestion.objects.filter(term=term,
                        exam_type=ex.exam_type,
                        session=currse,
                        subject=subject,
                        klass=student.admitted_class)#student.admitted_class



                    myq=[]

                    for q in qstns:
                        myq.append(q.id)

                    qu=[]

                    qu= [item for item in myq  if item not in transid]


                    if qu == []:

                        return render_to_response('CBT/done.html')



                    uid = 0


                    uid = random.choice(qu)
                    tk=0

                    tk = tblquestion.objects.get(term=q.term,
                        exam_type=q.exam_type,
                        session=student.admitted_session,
                        subject=sub.subject,
                        klass=student.admitted_class,
                        id=uid)

                    cbtold(session=currse,
                        question=tk,
                        term=q.term,
                        exam_type=q.exam_type,
                        klass=student.admitted_class,
                        subject=subject,
                        student=student,
                        qstcode=tk.id).save()

                    tk1 =tk.qstn
                    opt = tbloptions.objects.filter(qstn=tk)
                    ans=''


                    cbtcurrentquestion(student=student,
                        term = term,
                        session=currse,
                        subject=subject,
                        exam_type=ex.exam_type,
                        number=1).save()

                    number=1

            elif fq==1:
                fq=cbtcurrentquestion.objects.get(student=student,
                    session=currse,
                    term=term,
                    subject=subject,
                    exam_type=ex.exam_type,)

                number=int(fq.number)

                try:
                    mqst =cbttrans.objects.get(student=student,session=currse,
                        term=term,
                        exam_type=ex.exam_type,
                        subject=subject,
                        no=number)

                    ans=mqst.stu_ans

                    tk = tblquestion.objects.get(term=term,
                        exam_type=ex.exam_type,
                        session=currse,
                        subject=subject,
                        klass=student.admitted_class,
                        id=mqst.qstcode)

                    tk1 =tk.qstn
                    opt = tbloptions.objects.filter(qstn=tk)

                    uid= tk.id

                except:

                    mqst =cbtold.objects.get(student=student,session=currse,
                        term=term,
                        exam_type=ex.exam_type,
                        subject=subject,
                        klass=student.admitted_class)

                    ans=''

                    tk = tblquestion.objects.get(term=term,
                        exam_type=ex.exam_type,
                        session=currse,
                        subject=subject,
                        klass=student.admitted_class,
                        id=mqst.qstcode)

                    tk1 =tk.qstn
                    img=tk.image
                    opt = tbloptions.objects.filter(qstn=tk)

                    uid= tk.id

            return render_to_response('CBT/pupiltest.html',{'question':tk1,
                'school':school,
                'count':number,
                'image':img,
                'ans':ans,
                'form':student,
                'session':currse,
                'name':student.fullname,
                'klass':student.admitted_class,
                'adm':student.admissionno,
                'options':opt,
                'term':term,
                'uid':uid,
                'subject':subject})



        else:
            return HttpResponseRedirect('/login/')
    else:
        return HttpResponseRedirect('/login/')


def getcbtsubject(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                session,klass = acccode.split(':')
                kk = []
                sdic = {}
                data = tblcbtuser.objects.filter(session=session,klass = klass,user = varuser )
                for j in data:
                    j = j.subject
                    #print j
                    s = {j:j}
                    sdic.update(s)
                klist = sdic.values()
                for p in klist:
                   # print 'The Subject :',p
                    kk.append(p)
                return HttpResponse(json.dumps(kk), mimetype='application/json')
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def ajaxclass(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                # state = acccode
                kk = []
                sdic = {}
                data = tblcbtuser.objects.filter(user = varuser,session = acccode).order_by('klass')
                for j in data:
                    j = j.klass
                    s = {j:j}
                    sdic.update(s)
                klist = sdic.values()
                for p in klist:
                    kk.append(p)
                return HttpResponse(json.dumps(kk), mimetype='application/json')
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')


def exxxam(request):
	if "userid" in request.session:
		varuser=request.session['userid']
		pop =Student.objects.filter(fullname=varuser,admitted_session=currse,gone=False)

		return render_to_response('CBT/cbt.html',{'varuser':varuser,
			'sch':school,
			'pop':pop})
	else:
		return HttpResponseRedirect('/login/')



def beefore(request):
    if "userid" in request.session:
        if request.method=='POST':
            varuser=request.session["userid"]
            student= Student.objects.get(fullname=varuser,admitted_session=currse,gone=False)

            subject=tblcbtsubject.objects.get(klass=student.admitted_class,
                term=term,
                session=student.admitted_session,
                status='ACTIVE') #basic science

            subject=subject.subject

            qc=cbtcurrentquestion.objects.get(student=student,
                term =term,
                subject=subject,
                session=currse,
                exam_type=ex.exam_type)

            number=int(qc.number)

            image='image'


            if number==1:

                try:
                    pik = cbttrans.objects.get(student=student,session=currse,term=term,
                    exam_type=ex.exam_type,no=number,subject=subject)
                    ans=pik.stu_ans
                except:
                    pik=cbtold.objects.get(student=student,
                        session=currse,
                        term=term,
                        klass=student.admitted_class,
                        subject=subject,
                        exam_type=ex.exam_type)
                    ans=''
            else:
                n2=number-1
                pik = cbttrans.objects.get(student=student,session=currse,term=term,
                exam_type=ex.exam_type,no=n2,subject=subject)
                ans=pik.stu_ans

                hl=cbtcurrentquestion.objects.filter(student=student,
                    session=currse,
                    term = term,
                    subject=subject,
                    exam_type=ex.exam_type,
                    number=number).update(number=n2)
                number=n2

            tk = tblquestion.objects.get(session=currse,term=term, klass=student.admitted_class,
                exam_type=ex.exam_type, subject=subject,id=pik.qstcode)


            tk1 =tk.qstn
            tk2=tk.id
            img=tk.image
            opt = tbloptions.objects.filter(qstn=tk)

            return render_to_response('CBT/pupiltest.html',{'question':tk1,
                'school':school,
                'count':number,
                'ans':ans,
                'image':img,
                'form':student,
                'session':currse,
                'name':student.fullname,
                'klass':student.admitted_class,
                'adm':student.admissionno,
                'options':opt,
                'term':term,
                'uid':tk.id,
                'subject':subject})

        else:
            return HttpResponseRedirect('/welcome/')
    else:
        return HttpResponseRedirect('/login/')



def next(request):
    if "userid" in request.session:
        if request.method=='POST':
            varuser=request.session['userid']
            student=Student.objects.get(admitted_session=currse,fullname=varuser,gone=False)

            sub=tblcbtsubject.objects.get(klass=student.admitted_class,session=currse,status='ACTIVE')
            subject=sub.subject

            qwe=tblquestion.objects.filter(session=currse,
                term=term, klass=student.admitted_class,subject=subject,
                exam_type=ex.exam_type,section='A').count()

            qc=cbtcurrentquestion.objects.get(student=student,
                term =term,
                subject=subject,
                session=currse,
                exam_type=ex.exam_type)

            number=int(qc.number)

            if 'gender' in request.POST:
                a= request.POST['gender']


                try:
                    dt = cbttrans.objects.get(student=student,session=currse,term=term,
                        exam_type=ex.exam_type,no=number,subject=subject)

                    ty='update'
                except:

                    dt=cbtold.objects.get(student=student,session=currse,
                        term=term,exam_type=ex.exam_type,
                        klass=student.admitted_class,subject=subject)

                    ty='save'

                selq= tblquestion.objects.get(session=currse,term=term,
                    exam_type=ex.exam_type,klass=student.admitted_class,
                    subject= subject,id=dt.qstcode)

                sek=selq.qstn
                ans=tblans.objects.get(qstn=selq)
                ans=ans.ans
                b=str(ans)


                opti = tbloptions.objects.get(qstn=selq)
                d=opti.a
                e=opti.b
                g=opti.c
                w=opti.d

                if a == b: # if my answer is correct
                    if ty=='update':
                        k=cbttrans.objects.filter(student=student,session=currse,term=term,
                            exam_type=ex.exam_type,qstcode=selq.id,
                            subject=subject,).update(score =1,stu_ans=a)

                    elif ty=='save':

                        k=cbttrans(student=student,session=currse,term=term,
                            exam_type=ex.exam_type,question=selq,stu_ans=a, score = 1,
                            no=number,qstcode=selq.id,subject=subject).save()
                else:#if my ans is wrong

                    if a == str(d) or a == str(e) or a == str(g) or a == str(w):
                        if ty=='update':
                            cbttrans.objects.filter(student=student,session=currse,term=term,exam_type=ex.exam_type,
                                qstcode=selq.id,subject=subject).update(score=0,stu_ans=a)

                        elif ty=='save':
                            cbttrans(student=student,term=term, exam_type=ex.exam_type,question=selq,
                                stu_ans=a, score = 0,no=number,status=0,qstcode=selq.id,subject=subject,
                                session=currse).save()
                    else:
                        ty='whales'
                        tk = selq
                        ans=''

### porting to reportsheet module****************
                add=cbttrans.objects.filter(student=student,session=currse,term=term,
                        exam_type=ex.exam_type,
                        subject=subject).aggregate(Sum('score'))

                add = add['score__sum']

                acaderec = StudentAcademicRecord.objects.get(student = student, term=term)

        #               remove this line when you are ready
                subject ='SCIENCE'

                if ex.exam_type=='Welcome back':
                    subsco = SubjectScore.objects.filter(academic_rec = acaderec,
                        subject=subject,term=term,session=currse).update(first_ca=add)


                if ty == 'save': #if i added a new entry to cbttrans
                    subject='BASIC SCIENCE'
                    hu=cbtold.objects.get(session=currse,term=term,exam_type=ex.exam_type,klass=selq.klass,
                        subject=subject,student=student).delete()


                    trans=cbttrans.objects.filter(session=student.admitted_session,
                        exam_type=ex.exam_type,
                        student=student, #or student.id
                        subject=subject,
                        term=term)

                    count=trans.count()+1

                    transid=[]

                    for k in trans:
                            fb= k.qstcode.split('-')[0]
                            fb=int(fb)
                            transid.append(fb)


                    qstns=tblquestion.objects.filter(term=term,
                            exam_type=ex.exam_type,
                            session=student.admitted_session,
                            subject=subject,
                            klass=student.admitted_class)#student.admitted_class


                    myq=[]

                    for q in qstns:
                            myq.append(q.id)

                    qu=[]

                    qu= [item for item in myq  if item not in transid]


                    if qu == []:
                          cbtcurrentquestion.objects.filter(student=student,session=currse,term=term,
                                exam_type=ex.exam_type,
                                subject=subject).delete()
                          return render_to_response('CBT/done.html')

                    uid = 0


                    uid = random.choice(qu)
                    tk=0

                    tk = tblquestion.objects.get(term=q.term,
                            exam_type=q.exam_type,
                            session=student.admitted_session,
                            subject=subject,
                            klass=student.admitted_class,
                            id=uid)

                    gh=cbtold.objects.filter(session=currse,
                            question=tk,
                            term=term,
                            exam_type=ex.exam_type,
                            klass=student.admitted_class,
                            subject=subject,
                            student=student,
                            qstcode=tk.id).count()

                    if gh==0:
                        cbtold(session=currse,
                                question=tk,
                                term=term,
                                exam_type=ex.exam_type,
                                klass=student.admitted_class,
                                subject=subject,
                                student=student,
                                qstcode=tk.id).save()

                        n2=number+1
                        hj= cbtcurrentquestion.objects.filter(student=student,
                            term = term,
                            session=currse,
                            subject=subject,
                            exam_type=ex.exam_type,
                            number=number).update(number=n2)


                elif ty=='update':     #if i updated

                    try:
                        c='i update'

                        n2=number+1
                        subject='BASIC SCIENCE'

                        hj= cbtcurrentquestion.objects.filter(student=student,
                            term = term,
                            session=currse,
                            subject=subject,
                            exam_type=ex.exam_type,
                            number=number).update(number=n2)

                        qs= cbttrans.objects.get(student=student,session=currse,
                            term=term,exam_type=ex.exam_type,no=n2,subject=subject)
                        ans=qs.stu_ans

                        tk = tblquestion.objects.get(term=term,
                        exam_type=ex.exam_type,
                        session=currse,
                        subject=subject,
                        klass=student.admitted_class,
                        id=qs.qstcode)

                    except:

                        n2=number+1
                        subject='BASIC SCIENCE'

                        hj= cbtcurrentquestion.objects.filter(student=student,
                            term = term,
                            session=currse,
                            subject=subject,
                            exam_type=ex.exam_type,
                            number=number).update(number=n2)

                        qs=cbtold.objects.get(student=student,
                            session=currse,
                            term=term,
                            exam_type=ex.exam_type,
                            klass=student.admitted_class,
                            subject=subject)
                        ans=''

                        tk = tblquestion.objects.get(term=term,
                        exam_type=ex.exam_type,
                        session=currse,
                        subject=subject,
                        klass=student.admitted_class,
                        id=qs.qstcode)

                if ty != 'whales':
                    number=number+1

            else: #if i didnt chose an option
                try:
                    qs = cbttrans.objects.get(student=student,session=currse,term=term,
                        exam_type=ex.exam_type,no=number,subject=subject)
                    ans=qs.stu_ans

                except:

                    qs=cbtold.objects.get(student=student,session=currse,term=term,
                        exam_type=ex.exam_type,klass=student.admitted_class,subject=subject)
                    ans=''


                tk = tblquestion.objects.get(term=term,
                        exam_type=ex.exam_type,
                        session=currse,
                        subject=subject,
                        klass=student.admitted_class,
                        id=qs.qstcode)

            tk1 =tk.qstn
            opt = tbloptions.objects.filter(qstn=tk)



            return render_to_response('CBT/pupiltest.html',{'question':tk1,
                'school':school,
                'count':number,
                'form':student,
                'ans':ans,
                'session':currse,
                'name':student.fullname,
                'klass':student.admitted_class,
                'adm':student.admissionno,
                'options':opt,
                'term':term,
                'uid':tk.id,
                'subject':subject})

        else:
            return HttpResponseRedirect('/cbt/take_test/start/')
    else:
        return HttpResponseRedirect('/login/')
