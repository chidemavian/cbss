# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.http import  Http404, HttpResponseRedirect, HttpResponse
from django.core.serializers.json import json
from assessment.forms import *
from academics.models import *
from CBT.models import *
from sysadmin.models import *
from setup.models import *
from bill.utils import *
from assessment.getordinal import *
from assessment.utils import *
from assessment.bsheet import *
from lesson.models import *
from utilities.views import *
from django.db.models import Max,Sum
from assignment.models import *
import datetime
from datetime import date
import locale
locale.setlocale(locale.LC_ALL,'')
import xlwt
import decimal

#gh = tblrunp.objects.all().delete()
currse = currentsession.objects.get(id = 1)

sublists=[]

date=datetime.date.today()

#import south
#from south.models import *
#MigrationHistory.objects.all().delete()

# session='2023/2024'
# pp = tblrunp.objects.filter(session = session)
# fg= pp.filter(term= 'Second')
# fg.delete()


def wel(request):

    if  "userid" in request.session:
        varuser=request.session['userid']
        staff = userprofile.objects.get(username = varuser,status = "ACTIVE")

        if staff.createuser==1:
            return render_to_response('assessment/success.html',{'varuser':varuser})
        ttt= ClassTeacher.objects.filter(teachername=varuser)
        if ttt.count() > 0:
            return render_to_response('assessment/success_cl.html',{'varuser':varuser})
        else:
            return render_to_response('assessment/success_t.html',{'varuser':varuser})

    else:
        return HttpResponseRedirect('/login/')



def weld(request):
    klass=['JS 1', 'JS 2', 'JS 3']
    armz= ['A','B','C']

    all_subjcts = Subject.objects.filter(category = 'JS')

    for k in klass:
        for arm in armz:

            all_students= Student.objects.filter(admitted_session='2021/2022',
                admitted_class = k,
                admitted_arm=arm,
                gone=0,
                second_term=1, )

         ########## Addresssing mid term scores***************8


            for s in all_students:

                admno1 = s.admissionno
                klass1 = s.admitted_class
                arm1 = s.admitted_arm
                session1 = s.admitted_session
                term1 = 'Second'

                myrec = StudentAcademicRecord.objects.get(student=s,
                    term=term1,
                    klass=k,
                    arm=arm,
                    session=session1)

                for subj in all_subjcts:
                    mysubject = SubjectScore.objects.get(academic_rec = myrec,
                        term = 'Second',
                        subject=subj.subject,
                        klass=klass1,
                        arm=arm1,
                        session='2021/2022')

                    mid_term_score = mysubject.first_ca  +  mysubject.second_ca + mysubject.third_ca
                    mysubject.mid_term_score = mid_term_score
                    mysubject.save()

                    msg = mysubject.mid_term_score,subj.subject,s.fullname
                    return render_to_response('assessment/selectloan.html',{'msg':msg})

           ##### studentaveragemid(admno1,term1,session1,klass1,arm1)*************

                subjectcnt = SubjectScore.objects.filter(academic_rec = myrec,
                    term = term1)

                totsub = subjectcnt.count()

                subcount = subjectcnt.aggregate(Sum('mid_term_score'))

                casum = subcount['mid_term_score__sum']

                staver=casum/int(totsub)

                myrec.stu_ave1=staver

                myrec.save()

         ########## classaveragemid(klass1,session1,term1,arm1)***************8


            acaderecp=StudentAcademicRecord.objects.filter(klass=k,
                session='2021/2022',
                arm=arm,
                term= 'Second')


            casum=0
            totsub=0
            midsum=0


            for dff in acaderecp:
                mysubject = SubjectScore.objects.filter(academic_rec = dff,
                    term = 'Second',klass=k,arm=arm,session='2021/2022')

                totsubject = mysubject.count()
                midsum =mysubject.aggregate(Sum('mid_term_score'))
                midsum = midsum['mid_term_score__sum']
                totsub=totsub+totsubject
                casum=casum+ midsum

            clasAve=casum/int(totsub)

            acaderecp.update(class_ave1=clasAve)
                # for subject1 in all_subjcts:
                #     subjectaveragemid(term1,session1,klass1,arm1,subject1)

    msg='DONE'

    return render_to_response('assessment/selectloan.html',{'msg':msg})



def mysubjects(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        if request.method=='POST':
            form = studentform(request.POST)
            return HttpResponseRedirect("/reportsheet/student/my_subject_page/")

        else:
            form= studentform()
        return render_to_response('assessment/subjectpage.html',{'form':form,'varuser':varuser})
    else:
        return HttpResponseRedirect('/login/')




def mysubjectpage(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        if request.method=='POST':
            form = stuform(request.POST)
            if form.is_valid():
                session=form.cleaned_data['session']
                term = form.cleaned_data['term']
                try:
                    chk=tblcf.objects.get(session=session,term=term)
                    chkdate = chk.deadline
                except:
                    chkdate = date
                #if date<= chkdate:
                #    return render_to_response('assessment/checkback.html',{'ckk':chkdate})
                data=Student.objects.get(fullname=varuser.upper(),admitted_session=currse,gone=False)
                replist=[]
                if StudentAcademicRecord.objects.get(student=data,term=term):
                    acaderec=StudentAcademicRecord.objects.filter(student=data,term=term)
                    subsco=SubjectScore.objects.filter(academic_rec=acaderec).order_by('subject_teacher')
                    return render_to_response('assessment/mysubjects.html',{'getdetails':subsco,
                        'varuser':varuser,
                        'data':data,
                        'term':term,
                        'stuid':data.id,
                        'ckk':chkdate})
    else:
        return HttpResponseRedirect('/login/')



def studentreportll(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.studentreport
        if ClassTeacher.objects.filter(teachername = varuser).count() == 0 :
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        form = studentreportform2()
        school = get_object_or_404(School, pk=1)
        student =''
        if request.method == 'POST':
            form = studentreportform2(request.POST, request.FILES)
            if form.is_valid():
                session= form.cleaned_data['session']
                klass= form.cleaned_data['klass']
                arm = form.cleaned_data['arm']
                # dayboarding = form.cleaned_data['dayboarding']
                filtermethod = form.cleaned_data['filtermethod']
                disclass =''
                disarm = ''
                #excelfile
                if filtermethod == 'Classroom':
                    student = Student.objects.filter(admitted_class = klass,admitted_arm = arm,admitted_session = session,gone = False).order_by('fullname')
                    disclass = klass
                    disarm = arm
                else:
                    msg = 'select classroom'
                    return render_to_response('assessment/selectloan.html',{'msg':msg})




                if form.cleaned_data['excelfile']:
                    response = HttpResponse(mimetype="application/ms-excel")
                    response['Content-Disposition'] = 'attachment; filename=studentlist.xls'
                    wb = xlwt.Workbook()
                    ws = wb.add_sheet('studentlist')
                    ws.write(0, 4, school.name)
                    ws.write(1, 4, school.address)
                    ws.write(2, 2, '%s %s :: Student List for %s Session' %(disclass,disarm, session) )
                    ws.write(3, 0, 'Name')
                    ws.write(3, 1, 'Sex')
                    ws.write(3, 2, 'Admission No')
                    ws.write(3, 3, 'Class')
                    ws.write(3, 4, 'Arm')
                    ws.write(3, 5, 'House')
                    ws.write(3, 6, 'Day/Boarding')
                    ws.write(3, 7, 'Phone Number')
                    ws.write(3, 8, 'E-Mail')
                    k = 4
                    for jd in student:
                       ws.write(k, 0, jd.fullname)
                       ws.write(k, 1, jd.sex)
                       ws.write(k, 2, jd.admissionno)
                       ws.write(k, 3, jd.admitted_class)
                       ws.write(k, 4, jd.admitted_arm)
                       ws.write(k, 5, jd.house)
                       ws.write(k, 6, jd.dayboarding)
                       ws.write(k, 7, jd.fathernumber)
                       ws.write(k, 8, jd.fatheremail)
                       k += 1
                    wb.save(response)
                    return response
                else:
                    return render_to_response('assessment/student_list2.html', {
                      # 'p1':p1,'p2':p2,
                      'form': form,'school':school,'varuser':varuser,'students_list':student,'session':session,'disclass':disclass,'disarm':disarm}, RequestContext(request))
            else:
                 varerr = 'All Fields Are Required !'
                 return render_to_response('assessment/student_list.html', {'form': form,'school':school,'varerr':varerr}, RequestContext(request))
        else:
            form = studentreportform2()
            return render_to_response('assessment/student_list.html', {'varuser':varuser,'form': form,'school':school}, RequestContext(request))
    else:
        return HttpResponseRedirect('/login/')


def my_results(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        form= studentresultform()
        return render_to_response('assessment/resultpage.html',{'form':form,'varuser':varuser})
    else:
        return HttpResponseRedirect('/login/')


def my_results_page_detailed(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        if request.method=='POST':
            form = studentresultform(request.POST)
            if form.is_valid():
                session=form.cleaned_data['session']
                report = form.cleaned_data['report']
                term= request.POST['term']
                school=School.objects.get(id =1)


                if term == 'First':
                    next_term = tblterm.objects.get(term = 'Second')
                    next_term=next_term.start_date

                    try:

                        student = Student.objects.get(admitted_session =session,
                            first_term = 1,
                            fullname=varuser,
                            gone = False)

                    except:
                        msg = 'You do not have first term records'
                        return render_to_response('assessment/selectloan_student.html',{'msg':msg,'user':varuser})

                if term == 'Second':
                    next_term = tblterm.objects.get(term = 'Third')
                    next_term=next_term.start_date

                    try:

                        student = Student.objects.get(admitted_session =session,
                             second_term = 1,
                            fullname=varuser,
                            gone = False)

                    except:
                        msg = 'You do not have first term records'
                        return render_to_response('assessment/selectloan_student.html',{'msg':msg,'user':varuser})


                if term == 'Third':
                    next_term = tblterm.objects.get(term = 'First')
                    next_term=next_term.start_date

                    try:

                        student = Student.objects.get(admitted_session =session,
                            third_term = 1,
                            fullname=varuser,
                            gone = False)

                    except:
                        msg = 'You do not have first term records'
                        return render_to_response('assessment/selectloan_student.html',{'msg':msg,'user':varuser})





                klass = student.admitted_class

                arm=student.admitted_arm



                addklass=student.admitted_class
                varbeg=addklass[0]
                getgrading = gradingsys.objects.filter(classsub__startswith = varbeg)


                try:
                    chk=tblresult.objects.get(session=session,reportsheet=report, term=term)
                except:
                    varerr= 'Date not set, contact your home room teacher'
                    return render_to_response('assessment/notset.html',{'varerr':varerr})

                chkdate = chk.deadline

                if date < chkdate:
                    msg = 'Results are being compiled, kindly check back on'
                    msg2 = chk.deadline
                    return render_to_response('assessment/checkback.html',{'varuser':varuser,'msg':msg,'msg1':msg2})



                if report== 'End term':


                    gh = tblrunp.objects.filter(session = session,
                        klass=klass,
                        term=term,
                        arm=arm, reportsheet='End term')

                    gh_count =gh.count()

                    dddt = datetime.datetime.now()
                    mytime = dddt.time()


                    if gh_count == 1:
                        gh_new = gh.get(session=session,
                            klass=klass,
                            arm=arm,
                            term=term,
                            reportsheet='End term')

                        if gh_new.status == 1:
                            endtermstats(session,term,klass,arm)


                        gh_new.status=0
                        # gh_new.time=mytime
                        gh_new.save()

                    else:

                        tblrunp(session = session,
                            klass=klass,
                            term=term,
                            arm=arm,
                            time=mytime,
                            status = 0,
                            reportsheet='End term').save()

                        endtermstats(session,term,klass,arm)



                    acaderec = StudentAcademicRecord.objects.get(student = student,term = term)
                    sycho = PsychomotorSkill.objects.get(academic_rec = acaderec)#,term=term)
                    # affective= AffectiveSkill.objects.get(academic_rec=student)#,term=term)


                    subsco = SubjectScore.objects.filter(academic_rec = acaderec).order_by('num')


                    totsub  = subsco.count()


                    replist = []

                    if term == 'Third':
                        h=9
                        ssu =0
                        ssa=0
                        ssp=0

                        ## Times school opened**********
                        fg = tblterm.objects.filter(session=session)
                        for g in fg:
                            ssu = ssu+ int(g.duration)


                        next_term = tblterm.objects.get(term = 'First')
                        ntb=next_term.start_date

                        class_scores = 0
                        allkt = 0
                        sum_of_subject_averages=0
                        sum_of_subject_averages_class=0

                        subject_total=0


                        # for j in stuinfo:

                        acadep = StudentAcademicRecord.objects.filter(student = student,session=session)

                        if acadep.count() == 0:
                            ssa = 0
                            ssp=0
                        else:
                            ssa = acadep.aggregate(Sum('days_absent'))
                            ssa = ssa['days_absent__sum']

                            ssp = acadep.aggregate(Sum('days_present'))
                            ssp = ssp['days_present__sum']



                        acaderec = acadep.get(term = term)
                        affskill = AffectiveSkill.objects.get(academic_rec = acaderec)
                        psycho = PsychomotorSkill.objects.get(academic_rec = acaderec)
                        subsco = SubjectScore.objects.filter(academic_rec = acaderec,term = term,session = session).order_by('num')




                        firstrec='False'  ##OBTAINING FIRST TERM RECORDS *******************
                        secrec='False'
                        try:
                            acaderec1 = StudentAcademicRecord.objects.get(student = j,term = 'First',session=session)
                        except:
                            firstrec='True'


                        try:
                            acaderec2 = StudentAcademicRecord.objects.get(student = j,term = 'Second',session=session)
                        except:
                            secrec='True'

                        secsublist = []
                        secdic = {}

                        for h in subsco:
                            if firstrec=='True':
                                fscore = '-'
                            else:
                                try:

                                    fsc = SubjectScore.objects.get(session=session, academic_rec = acaderec1,term = 'First',subject = h.subject)
                                    fsco = fsc.end_term_score
                                    fscore = str(fsco)
                                except:
                                    fscore='-'

                            if secrec=='True':
                                fscoret = '-'
                            else:
                                try:
                                    fsct = SubjectScore.objects.get(session=session, academic_rec = acaderec2,term = 'Second',subject = h.subject)
                                    fscot = fsct.end_term_score
                                    fscoret = str(fscot)
                                except:
                                    fscoret = '-'
                            secdic ={'thirdterm':h,'firstterm':fscore,'secondterm':fscoret}
                            secsublist.append(secdic)





                        rtotals=0
                        totalmark = SubjectScore.objects.filter(academic_rec = acaderec,session = session,term = term).aggregate(Sum('end_term_score'))
                        totalmark2 = totalmark['end_term_score__sum']
                        rtotals = int(totalmark2)



                        #******total for first term*********************

                        totalmark2sec = 0
                        rtotalsec = 0


                        if firstrec=='False':# IE IF FIRST TERM RECORD IS FOUND
                            totalmarksec = SubjectScore.objects.filter(academic_rec = acaderec1,session = session,term = 'First').aggregate(Sum('end_term_score'))
                            totalmark2sec = totalmarksec['end_term_score__sum']
                            try:
                                rtotalsec = int(totalmark2sec)
                            except:
                                rtotalsec = 0
                        else:
                            rtotalsec = 0


                        #*******total for second term***************************
                        totalmark2sec1 = 0
                        rtotalsec1 = 0

                        if secrec=='False':#IE SECOND TERM RECORD IS FOUND
                            totalmarksec1 = SubjectScore.objects.filter(academic_rec = acaderec2,session = session,term = 'Second')
                            if totalmarksec1.count()>0:
                                totalmarksec1=totalmarksec1.aggregate(Sum('end_term_score'))
                                totalmark2sec1 = totalmarksec1['end_term_score__sum']
                                rtotalsec1 = int(totalmark2sec1)
                            else:
                                rtotalsec1 =0

                        else:
                            rtotalsec1 = 0

                        #*************************#annual average********************
                        totalmark24 = 0
                        rtotal4 = 0
                        totalmark4 = SubjectScore.objects.filter(academic_rec = acaderec,session = session,term = term).aggregate(Sum('end_term_score'))
                        totalmark24 = totalmark4['end_term_score__sum']
                        rtotal4 = float(totalmark24)



                        stave=subsco.count()
                        stave=rtotal4 / stave


                        if varbeg == 'S':
                            st_grade = studentaveragedrader(float(stave))  #grading student average
                        elif varbeg=='J':
                            st_grade = juniorgrade(float(stave))


                        stat={'st_grade':st_grade['grade']}


                        # t2t=Annual_statistics(session,j.admitted_class,j.admitted_arm,j.admissionno)

                        t2t=Annual_statistics(session,student.admitted_class,student.admissionno)

                        perf=[]


                        kt= 0
                        tottal_scores = 0

                        allfirst=0
                        allsecond=0
                        allthird =0


                        for subject in t2t:

                            acaderec = acadep.filter(term = 'First')
                            if acaderec.count()==1:
                                acaderec=acaderec.get()
                                p1= SubjectScore.objects.filter(session = session, academic_rec = acaderec,subject=subject,term='First')
                                if p1.count()==1:
                                    p1=p1.get()
                                    pf=p1.end_term_score
                                    if pf =='0':
                                        kt =kt +0
                                    else:
                                        kt =kt +1
                                    tottal_scores= tottal_scores+ int(pf)
                                    allfirst= allfirst + int(pf)
                                else:
                                    pf='N/A'
                            else:
                                pf ='N/A'


                            acaderec = acadep.filter(term = 'Second')
                            if acaderec.count() ==1:
                                acaderec=acaderec.get()
                                p2= SubjectScore.objects.filter(session = session, academic_rec = acaderec,subject=subject,term='Second')
                                if p2.count()==1:
                                    p2=p2.get()
                                    ps=p2.end_term_score
                                    if ps == '0':
                                        kt =kt +0
                                    else:
                                        kt = kt + 1

                                    tottal_scores= tottal_scores+ int(ps)
                                    allsecond=allsecond + int(ps)
                                else:
                                    ps='N/A'
                            else:
                                ps='N/A'


                            acaderec = acadep.filter(term = 'Third')
                            if acaderec.count() ==1:
                                acaderec=acaderec.get()
                                p3= SubjectScore.objects.filter(session = session, academic_rec = acaderec,subject=subject,term='Third')
                                if p3.count()==1:
                                    p3=p3.get()
                                    pt=p3.end_term_score
                                    if pt == '0':
                                        kt =kt +0
                                    else:
                                        kt =kt +1
                                    tottal_scores= tottal_scores+ int(pt)
                                    allthird =allthird + int(pt)

                                else:
                                    pt='N/A'
                            else:
                                pt='N/A'


                            if kt==0:
                                ave=  0
                            elif kt > 0:
                                ave=  float(tottal_scores) / kt


                            if varbeg == 'S':
                                st_grade = studentaveragedrader(float(ave))  #grading student average
                            elif varbeg=='J':
                                st_grade = juniorgrade(float(ave))



                            d= {'subject':subject,
                            'first':pf,
                            'second':ps,
                            'third':pt,
                            'annual':locale.format("%.1f",ave,grouping=True),
                            'annual_grade':st_grade['grade'],
                            'annual_grade_remark':st_grade['remark']}

                            perf.append(d)

                            sum_of_subject_averages=sum_of_subject_averages + ave

                            sum_of_subject_averages_class=sum_of_subject_averages_class + ave

                            class_scores = class_scores+ tottal_scores
                            allkt =allkt + kt
                            tottal_scores = 0
                            kt = 0

                        annual_class_avg = class_scores / allkt

                        an_sc = allfirst + allsecond + allthird


                        an_avg= sum_of_subject_averages / len(t2t)

                        subject_total = subject_total + len(t2t)




                        if varbeg == 'S':
                            an_grade = studentaveragedrader(float(an_avg))  #grading student average
                        elif varbeg=='J':
                            an_grade = juniorgrade(float(an_avg))



                        category = klass[0:2]
                        ggg=klass[-1]

                        coms=tblcom.objects.filter(category=category)
                        mid=[]

                        for cat in coms:
                            fb= cat.krang.split('-')[0]
                            fb=int(fb)
                            mid.append(fb)
                        mida=sorted(mid)
                        pos=0
                        pos=min(mida, key=lambda x:abs(x-float(an_avg)))
                        varerr='DONE WITH ZERO ERRORS'
                        coma=tblcom.objects.filter(krang__startswith=pos,category=category)
                        idvar=[]
                        for h in coma:
                            idvar.append(h.id)
                        idvar=idvar
                        uid=0
                        uid = random.choice(idvar)
                        esther=tblcom.objects.get(id=uid)


                        if ggg == '1':
                            nxt = category + " " + '2'
                        elif ggg == '2':
                            nxt = category + " " + '3'



                        if an_grade['grade']=='F':
                            comment = esther.comment + ' Advice to repeat'
                        else:
                            comment=esther.comment + ' Promoted to ' + nxt









                        tt={'total':perf,
                            'total_score':tottal_scores,
                           'days_open':ssu,
                            'days_absent':ssa,
                            'days_present':ssp,
                            'totalfirst':allfirst,
                            'totalsecond':allsecond,
                            'totalthird':allthird,
                            'cummulative_comment':comment,
                            'total_subject_avg':locale.format("%.2f",sum_of_subject_averages,grouping=True),
                            'an_avg':locale.format("%.1f",an_avg,grouping=True),
                            'an_grade':an_grade['grade']}





                        #**********************************************
                        jdic = {'studentinfo':student,
                        'academic':acaderec,
                        'affective':affskill,
                        'sycho':psycho,
                        'subject':secsublist,
                        'st_grade':stat,
                        'totalmark':rtotals,
                        'totalmark1':rtotalsec,
                        'totalmark2':rtotalsec1,
                        'annualavg':locale.format("%.2f",rtotal4,grouping=True),
                        'getgrading':getgrading}


                        k = {'summary':jdic,'cummulative':tt}
                        replist.append(k)





                        an_avg=0
                        sum_of_subject_averages= 0





                        overall_class_avg = sum_of_subject_averages_class / subject_total

                        if klass[0] == 'S':
                            # if form.cleaned_data['pdffile']:
                            #     template ='assessment/reportviewthirdsss.html'
                            #     context = {'form':form,'varerr':varerr,'replist':replist,'school':school,'term':term,'stuno':stuno}
                            #     return render_to_pdf(template, context)
                            # else:
                            return render_to_response('assessment/reportthirdsss.html',
                                {'varerr':varerr,'replist':replist,
                                'annual_class_avg':locale.format("%.1f",annual_class_avg,grouping=True),
                                'school':school,'date':date,'term':term,'next':ntb})


                        elif klass[0] == 'N' or klass[0] == 'C' or klass[0] == 'L':
                            # if form.cleaned_data['pdffile']:
                            #     template ='assessment/reportnviewthird.html'
                            #     context = {'form':form,'varerr':varerr,'replist':replist,'school':school,'term':term,'stuno':stuno,'classavg':locale.format("%.2f",clavg,grouping=True)}
                            #     return render_to_pdf(template, context)
                            # else:
                            return render_to_response('assessment/reportnthirde.html',{'form':form,'varerr':varerr,'replist':replist,'date':date,'school':school,'term':term,'stuno':stuno,'classavg':locale.format("%.2f",clavg,grouping=True)})

                        else:
                            # if form.cleaned_data['pdffile']:
                            #     template ='assessment/reportviewthird.html'
                            #     context = {'form':form,'varerr':varerr,'replist':replist,'school':school,'term':term,'stuno':stuno,'classavg':locale.format("%.2f",clavg,grouping=True)}
                            #     return render_to_pdf(template, context)
                            # else:
                            return render_to_response('assessment/reportthird.html',
                                {'varerr':varerr,
                                'varuser':varuser,
                                'replist':replist,
                                'school':school,
                                'date':date,
                                'term':term,
                                'annual_class_avg':locale.format("%.1f",annual_class_avg,grouping=True),
                                'next':ntb})

                    else:
                        if varbeg == 'J' :

                            return render_to_response('assessment/my_results.html',{'varuser':varuser,
                                    'school':school,
                                    'date':date,
                                    'replist':replist,
                                    'term':term.upper(),
                                    'next_term':next_term})

                        elif varbeg== 'S' :
                            return render_to_response('assessment/ssreults.html',{'varuser':varuser,
                                    'school':school,
                                    'date':date,
                                    'replist':replist,
                                    'term':term.upper(),
                                    'next_term':next_term})
                elif report== 'Mid term' :


                    acaderec = StudentAcademicRecord.objects.get(student = student,term = term)
                    sycho = PsychomotorSkill.objects.get(academic_rec = acaderec)#,term=term)
                    # affective= AffectiveSkill.objects.get(academic_rec=student)#,term=term)
                    subsco = SubjectScore.objects.filter(academic_rec = acaderec).order_by('num')
                    totsub = subsco.count()

                    replist = []
                    totsub = 0
                    msublist = []
                    stustat=[]
                    stave=acaderec.stu_ave1 * 5 #student ave based on mid term
                    clave =acaderec.class_ave1 * 5  #student ave based on end term


                    if varbeg == 'S':
                        remark = studentaveragedrader(float(stave))
                    elif varbeg=='J':
                        remark = juniorgrade(float(stave))
                    remark=remark['grade']



                    stat={'stave':stave,'clave':clave,'st_grade':remark}
                    stustat.append(stat)

                    for jj in subsco:  ###grade each subject..............................
                        mymid = int(jj.mid_term_score) * 5
                        if varbeg == 'S':
                            remark = seniorgrade(float(mymid))
                        elif varbeg=='J':
                            remark = juniorgrade(float(mymid))
                        msub = {'subject':jj.subject,
                        'mid_term':jj.mid_term_score,
                        'totalperc':mymid,
                        # 'totalperc':locale.format("%.0f",mymid,grouping=True),
                        'remark':remark['remark'],
                        'grade':remark['grade'],
                        'teacher':jj.subject_teacher}
                        msublist.append(msub)

                    #****************all i need in report******************************
                    jdic = {'date':date,
                    # 'codi':codi,
                    'studentinfo':student,
                    'stat':stustat,

                    'pyscho':sycho,
                    'academic':acaderec,
                    'subject':msublist,
                    'school':school}
                    replist.append(jdic)

                    return render_to_response('assessment/midterm.html',{'session':session,
                        'form':form,
                        'varuser':varuser,
                        # 'varerr':varerr,
                        'replist':replist,
                        'term':term.upper()})


        else:
            form = studentresultform()
            return render_to_response('assessment/resultpage.html',{'varuser':varuser,'form':form})

    else:
        return HttpResponseRedirect('/login/')


def my_results_page(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        if request.method=='POST':
            form = studentresultform(request.POST)
            if form.is_valid():
                session=form.cleaned_data['session']
                report = form.cleaned_data['report']
                term= request.POST['term']
                school=School.objects.get(id =1)


                if term == 'First':
                    next_term = tblterm.objects.get(term = 'Second')
                    next_term=next_term.start_date

                    try:

                        student = Student.objects.get(admitted_session =session,
                            first_term = 1,
                            fullname=varuser,
                            gone = False)

                    except:
                        msg = 'You do not have first term records'
                        return render_to_response('assessment/selectloan_student.html',{'msg':msg,'user':varuser})

                if term == 'Second':
                    next_term = tblterm.objects.get(term = 'Third')
                    next_term=next_term.start_date

                    try:

                        student = Student.objects.get(admitted_session =session,
                             second_term = 1,
                            fullname=varuser,
                            gone = False)

                    except:
                        msg = 'You do not have first term records'
                        return render_to_response('assessment/selectloan_student.html',{'msg':msg,'user':varuser})


                if term == 'Third':
                    next_term = tblterm.objects.get(term = 'First')
                    next_term=next_term.start_date

                    try:

                        student = Student.objects.get(admitted_session =session,
                            third_term = 1,
                            fullname=varuser,
                            gone = False)

                    except:
                        msg = 'You do not have first term records'
                        return render_to_response('assessment/selectloan_student.html',{'msg':msg,'user':varuser})







                addklass=student.admitted_class
                varbeg=addklass[0]
                getgrading = gradingsys.objects.filter(classsub__startswith = varbeg)


                try:
                    chk=tblresult.objects.get(session=session,reportsheet=report, term=term)
                except:
                    varerr= 'Date not set, contact your home room teacher'
                    return render_to_response('assessment/notset.html',{'varerr':varerr})

                chkdate = chk.deadline

                if date < chkdate:
                    msg = 'Results are being compiled, kindly check back on'
                    msg2 = chk.deadline
                    return render_to_response('assessment/checkback.html',{'varuser':varuser,'msg':msg,'msg1':msg2})


                acaderec = StudentAcademicRecord.objects.get(student = student,term = term)
                sycho = PsychomotorSkill.objects.get(academic_rec = acaderec)#,term=term)
                # affective= AffectiveSkill.objects.get(academic_rec=student)#,term=term)
                subsco = SubjectScore.objects.filter(academic_rec = acaderec).order_by('num')
                totsub = SubjectScore.objects.filter(academic_rec = acaderec).count()

                if report== 'End term':

                    if varbeg == 'S':
                        my_grade = studentaveragedrader(float(acaderec.stu_ave2))  #grading student average
                    elif varbeg=='J':
                        my_grade = juniorgrade(float(acaderec.stu_ave2))
                    my_grade=my_grade['grade']


                    replist = []

                    classtot = 0
                    totsub = 0
                    totalmarkcount = 0

                    totalmark2 = 0
                    totalmark = subsco.aggregate(Sum('end_term_score'))
                    totalmark2 = totalmark['end_term_score__sum']
                    rtotal = int(totalmark2) #total of term scores from all subject

                    jdic = {'school':school,
                    'studentinfo':student,
                    'stu_grade': my_grade,
                    'sycho':sycho,
                    'grading':getgrading,
                    'academic':acaderec,
                    'subject':subsco,
                    'totalmark':rtotal}
                    replist.append(jdic)


                    if varbeg == 'J' :

                        return render_to_response('assessment/my_results.html',{'varuser':varuser,
                                'school':school,
                                'date':date,
                                # 'varerr':varerr,
                                'replist':replist,
                                'term':term.upper(),
                                'next_term':next_term})

                    elif varbeg== 'S' :
                        return render_to_response('assessment/reportpin.html',{'varuser':varuser,
                                'school':school,
                                'date':date,
                                # 'varerr':varerr,
                                'replist':replist,
                                'term':term.upper(),
                                'next_term':next_term})


                elif report== 'Mid term' :
                    replist = []
                    totsub = 0
                    msublist = []
                    stustat=[]
                    stave=acaderec.stu_ave1 * 5 #student ave based on mid term
                    clave =acaderec.class_ave1 * 5  #student ave based on end term


                    if varbeg == 'S':
                        remark = studentaveragedrader(float(stave))
                    elif varbeg=='J':
                        remark = juniorgrade(float(stave))
                    remark=remark['grade']



                    stat={'stave':stave,'clave':clave,'st_grade':remark}
                    stustat.append(stat)


                    for jj in subsco:
                        mymid = int(jj.mid_term_score) * 5
                        if varbeg == 'S':
                            remark = seniorgrade(float(mymid))
                        elif varbeg=='J':
                            remark = juniorgrade(float(mymid))
                        msub = {'subject':jj.subject,
                        'mid_term':jj.mid_term_score,
                        'totalperc':mymid,
                        # 'totalperc':locale.format("%.0f",mymid,grouping=True),
                        'remark':remark['remark'],
                        'grade':remark['grade'],
                        'teacher':jj.subject_teacher}
                        msublist.append(msub)

                    #****************all i need in report******************************
                    jdic = {'date':date,
                    # 'codi':codi,
                    'studentinfo':student,
                    'stat':stustat,

                    'pyscho':sycho,
                    'academic':acaderec,
                    'subject':msublist,
                    'school':school}
                    replist.append(jdic)

                    return render_to_response('assessment/midterm.html',{'session':session,
                        'form':form,
                        'varuser':varuser,
                        # 'varerr':varerr,
                        'replist':replist,
                        'term':term.upper()})


        else:
            form = studentresultform()
            return render_to_response('assessment/resultpage.html',{'varuser':varuser,'form':form})

    else:
        return HttpResponseRedirect('/login/')

def my_scripts(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        if request.method=='POST':
            form = stuform(request.POST)
            if form.is_valid():
                session=form.cleaned_data['session']
                term=form.cleaned_data['term']
                try:
                    chk=tblcf.objects.get(session=session,term=term)
                    chkdate = chk.deadline
                except:
                    chkdate = date
                data=Student.objects.get(fullname=varuser.upper(),admitted_session=currse,gone=False)
                replist=[]
                if StudentAcademicRecord.objects.get(student=data,term=term):
                    acaderec=StudentAcademicRecord.objects.filter(student=data,term=term)
                    subsco=SubjectScore.objects.filter(academic_rec=acaderec).order_by('subject_teacher')

                else:
                    subsco= 'my head'
                    # pass

                for sub in subsco:
                    fb= sub.subject.split('-')[0]
                    fb=str(fb)
                    replist.append(fb)


                scripty=cbttrans.objects.filter(term=term,
                    student=data,
                    session=data.admitted_session,
                    subject='BASIC SCIENCE',
                    exam_type= 'Welcome back').aggregate(Sum('score'))

                add = scripty['score__sum']


                total=cbttrans.objects.filter(term=term,student=data,session=data.admitted_session, subject='BASIC SCIENCE',exam_type= 'Welcome back').count()



                script=cbttrans.objects.filter(term=term,student=data,session=data.admitted_session, subject='BASIC SCIENCE',exam_type= 'Welcome back')
                optionlist=[]
                for k in script:
                    quest=tblquestion.objects.get(id=k.qstcode, term=term,session=currse,klass=data.admitted_class,exam_type=k.exam_type,subject=k.subject)
                    opt=tbloptions.objects.filter(qstn=quest)
                    answer=tblans.objects.get(qstn=quest)
                    optdic={'question':k,'options':opt,'answer':answer}
                    optionlist.append(optdic)


                return render_to_response('assessment/allscripts.html',{'total':total,'add':add,'getdetails':optionlist,'term':term,'data':data})

        else:
            form= stuform()
        return render_to_response('assessment/myscripts.html',{'form':form,'varuser':varuser})
    else:
        return HttpResponseRedirect('/login/')


def myassess(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        form= studentform()
        return render_to_response('assessment/myassess.html',{'form':form,'varuser':varuser})
    else:
        return HttpResponseRedirect('/login/')


def stunotes(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        varerr='Lesson Notes'
        if request.method=='POST':
            form= myform(request.POST)
            # varerr='varerr'
            if form.is_valid():
                session=form.cleaned_data['session']
                term=form.cleaned_data['term']
                subject= form.cleaned_data['subject']
                data= Student.objects.get(admitted_session=session,fullname= varuser,gone=False)
                klass=data.admitted_class
                sett = tbltopic.objects.filter(klass = data.admitted_class,term = term, subject = subject)
                questions=[]
                for qst in sett:
                    sub=qst.subject
                    topic=qst.topic
                    note=str(qst.lessonnote)
                    note=note.split('/')[-1]
                    sett={'sub':sub,'topic':topic,'note':note}
                    questions.append(sett)
                return render_to_response('assessment/notes.html',{'sett':questions,'varuser':varuser ,'varerr':varerr, 'session':session,'term':term,'klass':klass,'subject':subject})
        else:
            form= myform()
        return render_to_response('assessment/stunotes.html',{'form':form,'varuser':varuser,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')


def getstusubject(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                session,term,varuser= acccode.split(':')
                kk = []
                sdic = {}
                stu = Student.objects.get(admitted_session=session,gone=False,fullname= varuser)
                acadec = StudentAcademicRecord.objects.get(student=stu,term=term)
                data = SubjectScore.objects.filter(academic_rec=acadec).order_by('subject')
                for j in data:
                    j = j.subject
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


def classlist(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        try:
            user = ClassTeacher.objects.get(username = varuser)
        except:
            if ClassTeacher.objects.filter(teachername = varuser).count() == 0 :
                return HttpResponseRedirect('/reportsheet/access-denied/')
        user = userprofile.objects.get(username = varuser)
        varerr =''
        getdetails =''
        form = caform()
        # term=term
        return render_to_response('assessment/classlist.html',{'varuser':varuser,'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')

def halfterm(request):
    if  "userid" in request.session:
        varuser = request.session['userid']

        user = userprofile.objects.get(username = varuser)
        uenter = user.createuser

        klassteacher = ClassTeacher.objects.filter(teachername=varuser).count()



        if uenter is False :
            if klassteacher == 0:
                return HttpResponseRedirect('/reportsheet/access-denied/')



        varerr =''
        getdetails =''
        school=School.objects.get(id =1)
        if request.method == 'POST':
            form = reportsheetform(request.POST)
            if form.is_valid():
                session = form.cleaned_data['session']
                klass = form.cleaned_data['klass']
                term = form.cleaned_data['term']
                arm = form.cleaned_data['arm']

                if term=='First':
                    stuinfo = Student.objects.filter(first_term=True,
                        admitted_session = session,
                        admitted_class = klass,
                        admitted_arm = arm, gone = False).order_by('fullname')
                elif term == 'Second':
                    stuinfo = Student.objects.filter(second_term=True,
                        admitted_session = session,
                        admitted_class = klass,
                        admitted_arm = arm, gone = False).order_by('fullname')
                elif term == 'Third':
                    stuinfo = Student.objects.filter(third_term=True,
                        admitted_session = session,
                     admitted_class = klass,
                     admitted_arm = arm, gone = False).order_by('fullname')
                try:
                  codi = ClassTeacher.objects.get(klass=klass,session=session,teachername='N/A')
                except:
                  codi='Not Available'

                replist = []
                varbeg = klass[0]


                for j in stuinfo: #students in a class
                    totsub = 0
                    acaderec = StudentAcademicRecord.objects.get(student = j,term = term)
                    psycho = PsychomotorSkill.objects.get(academic_rec = acaderec)
                    subsco = SubjectScore.objects.filter(academic_rec = acaderec,term=term).order_by('num')
                    # totsub =  SubjectScore.objects.filter(academic_rec = acaderec).count()
                    totsub =  subsco.count()
                    msublist = []
                    stustat=[]

                    stave=acaderec.stu_ave1 * 5 #student ave based on mid term
                    clave =acaderec.class_ave1 * 5  #student ave based on end term


                    if varbeg == 'S':
                        st_grade = studentaveragedrader(float(stave))
                    elif varbeg=='J':
                        st_grade = juniorgrade(float(stave))


                    stat={'stave':stave,'clave':clave,'st_grade':st_grade['grade']}
                    stustat.append(stat)

######......................grade each subject...............................
                    for jj in subsco:
                        mymid = int(jj.mid_term_score) * 5
                        mmm= int(jj.mid_term_score)

                        if varbeg == 'S':
                            remark = seniorgrade(float(mymid))
                        elif varbeg=='J':
                            remark = juniorgrade(float(mymid))

                        msub = {'subject':jj.subject,
                                'mid_term':mmm,
                                'totalperc':mymid,
                                'remark':remark['remark'],
                                'grade':remark['grade'],
                                'teacher':jj.subject_teacher}

                        msublist.append(msub)

                    #****************all i need in report******************************
                    jdic = {'date':date,
                                'codi':codi,
                                'studentinfo':j,
                                'stat':stustat,
                                'pyscho':psycho,
                                'academic':acaderec,
                                'subject':msublist,
                                'school':school}

                    replist.append(jdic)

                return render_to_response('assessment/midmid.html',{'session':session,
                    'form':form,
                    'varuser':varuser,
                    'varerr':varerr,
                    'replist':replist,
                    'term':term})

        else:
            form = reportsheetform()

            if klassteacher == 1:
                return render_to_response('assessment/halfterm.html',{'varuser':varuser,'form':form,'varerr':varerr})

            elif uenter==True:
                return render_to_response('assessment/halfterm_admin.html',{'varuser':varuser,'form':form,'varerr':varerr})

    else:
        return HttpResponseRedirect('/login/')




def getstudentlist(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                session,klass,arm,term = acccode.split(':')
                getstu = Student.objects.filter(admitted_class = klass,admitted_arm=arm,admitted_session = session,gone = False).order_by('fullname')
                return render_to_response('assessment/myclasslist.html',{'data':getstu,'term':term})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')


def stucourseform(request):
    if 'userid' in request.session:
        if request.is_ajax():
            if request.method=='POST':
                varuser=request.session['userid']
                post=request.POST.copy()
                acccode=post['userid']
                adm,term=acccode.split(':')
                getstu=Student.objects.get(admissionno=adm,admitted_session=currse,gone=False)
                rec=StudentAcademicRecord.objects.get(student=getstu,term=term)
                sub=SubjectScore.objects.filter(academic_rec=rec)
                return render_to_response('assessment/studentcf.html',{'getdetails':sub,'term':term})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')



def studentcourseform(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        varerr =""
        getstu = Student.objects.get(id=vid, admitted_session=currse,gone=False)
        teach= ClassTeacher.objects.get(teachername=varuser)
        form= cfform()
        if teach.klass==getstu.admitted_class:
            term = tblterm.objects.filter(status='ACTIVE')
            tr=[]
            for t in term:
                t=t.term
                tr.append(t)
            if StudentAcademicRecord.objects.filter(student = getstu):#,term = term):
               comm = StudentAcademicRecord.objects.filter(student = getstu)#,term = term)
               getdetails = SubjectScore.objects.filter(session = currse,klass = getstu.admitted_class, arm =getstu.admitted_arm,academic_rec = comm).order_by('num')
            return render_to_response('assessment/subgroup.html',{'form':form,'term':tr,'session':currse,'varuser':varuser,'getdetails':getdetails,'stuid':getstu.id,'getstu':getstu})
        else:
            return HttpResponseRedirect('/reportsheet/access-denied/')

    else:
        return HttpResponseRedirect('/login/')

def hgkvkuu(request,vid):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method=='POST':
                varuser = request.session['userid']
                varerr =""
                post=request.POST.copy()
                acccode= post['userid']
                vid,term=acccode.split(':')
                getstu = Student.objects.get(id=vid, admitted_session=currse)
                if StudentAcademicRecord.objects.filter(student = getstu,term = term):
                   comm = StudentAcademicRecord.objects.get(student = getstu,term = term)
                   getdetails = SubjectScore.objects.filter(session = currse,klass = getstu.admitted_class, arm = getsu.admitted_arm,term = term,academic_rec = comm).order_by('num')
                   return render_to_response('assessment/studentcf.html',{'varuser':varuser,'data':getdetails,'stuid':getstu.id,'fullname':getstu.fullname})
        else:
            HttpResponseRedirect('/login/')
    else:
        return HttpResponseRedirect('/login/')

def pq(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        varerr='Past Questions'
        if request.method=='POST':
            form= mypqform(request.POST)
            if form.is_valid():
                session=form.cleaned_data['session']
                term=form.cleaned_data['term']
                subject= form.cleaned_data['subject']
                klass= form.cleaned_data['klass']
                if Student.objects.get(admitted_session=session,fullname=varuser,gone=False):
                    sett = tblquest.objects.filter(klass = klass,term = term, session=session,subject = subject)
                    questions=[]
                    for qst in sett:
                        sub=qst.subject
                        qst=str(qst.question)
                        qst=qst.split('/')[-1]
                        sett={'sub':sub,'qst':qst}
                        questions.append(sett)
                    return render_to_response('assessment/pq.html',{'sett':questions,'varuser':varuser ,'varerr':varerr, 'session':session,'term':term,'klass':klass,'subject':subject})
        else:

            form= mypqform()
        return render_to_response('assessment/stupq.html',{'form':form,'varuser':varuser,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')




def castudent(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method=='POST':
                varuser = request.session['userid']
                varerr =''
                getdetails =''
                post= request.POST.copy()
                acccode=post['userid']
                term,session,ca = acccode.split(':')
                school=School.objects.get(id =1)
                stuinfo = Student.objects.get(admitted_session = session,fullname=varuser,gone = False)

                try:
                  codi = ClassTeacher.objects.get(klass=stuinfo.admitted_class,session=session,teachername='N/A')
                except:
                  codi = 'Not Entered'

                if ca == '1st Ca':
                    replist = []
                    varbeg = stuinfo.admitted_class[0]
                    acaderec = StudentAcademicRecord.objects.get(student = stuinfo,term = term)
                    psycho = PsychomotorSkill.objects.get(academic_rec = acaderec)
                    subsco = SubjectScore.objects.filter(academic_rec = acaderec).order_by('num')
                    totsub = SubjectScore.objects.filter(academic_rec = acaderec).count()
                    msublist = []
                    for jj in subsco:
                        fca = jj.first_ca
                        totalperc1 = fca/20
                        totalperc = totalperc1 * 100
                        if varbeg == 'S':
                            remark = seniorgrade(float(totalperc))
                        else:
                            remark = juniorgrade(float(totalperc))

                        msub = {'subject':jj.subject,'first_ca':fca,'totalperc':locale.format("%.1f",totalperc,grouping=True),'remark':remark['remark'],'grade':remark['grade'],'teacher':jj.subject_teacher}
                        msublist.append(msub)
                        #****************all i need in report******************************
                    jdic = {'date':date,'codi':codi,'studentinfo':stuinfo,'academic':acaderec,'pyscho':psycho,'subject':msublist}
                    replist.append(jdic)
                    return render_to_response('assessment/myassessajax.html',{'session':session,'varuser':varuser,'varerr':varerr,'replist':replist,'school':school,'term':term})

                elif ca == '2nd Ca':
                    replist = []
                    varbeg = stuinfo.admitted_class[0]
                    acaderec = StudentAcademicRecord.objects.get(student = stuinfo,term = term)
                    psycho = PsychomotorSkill.objects.get(academic_rec = acaderec)
                    subsco = SubjectScore.objects.filter(academic_rec = acaderec).order_by('num')
                    totsub = SubjectScore.objects.filter(academic_rec = acaderec).count()
                    msublist = []
                    for jj in subsco:
                        sca = jj.second_ca
                        totalperc1 = sca/20
                        totalperc = totalperc1 * 100
                        if varbeg == 'S':
                            remark = seniorgrade(float(totalperc))
                        else:
                            remark = juniorgrade(float(totalperc))

                        msub = {'subject':jj.subject,'second_ca':sca,'totalperc':locale.format("%.1f",totalperc,grouping=True),'remark':remark['remark'],'grade':remark['grade'],'teacher':jj.subject_teacher}
                        msublist.append(msub)
                        #****************all i need in report******************************
                    jdic = {'date':date,'codi':codi,'studentinfo':stuinfo,'academic':acaderec,'pyscho':psycho,'subject':msublist}
                    replist.append(jdic)

                    return render_to_response('assessment/stuassess.html',{'session':session,'varuser':varuser,'varerr':varerr,'replist':replist,'school':school,'term':term})

                else:
                    return render_to_response('index.html')
        else:
            return render_to_response('index.html')
    else:
        return HttpResponseRedirect('/login/')


def mybills(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        form= studentform()
        return render_to_response('assessment/mybills.html',{'form':form,'varuser':varuser})
    else:
        return HttpResponseRedirect('/login/')

def printmybill(request):
    if 'userid' in request.session:
        varuser = request.session['userid']
        varerr = ''
        getdetails = ''
        school = get_object_or_404(School, pk = 1)
        if request.method == 'POST':
            form = stuform(request.POST)
            if form.is_valid():
                session = form.cleaned_data['session']
                term = form.cleaned_data['term']
                bill_list = []
                # studata = Student.objects.filter(fullname =varuser, admitted_session = session, gone = False)
                studata = Student.objects.get(fullname =varuser, admitted_session = session, gone = False)
                varrid2 = 0
                getaddbill = ''
                billlist = []
                if tblbill.objects.filter(klass = studata.admitted_class, term = term, dayboarding = studata.dayboarding).count() == 0:
                    varrid = 0
                else:
                    getbill = tblbill.objects.filter(klass = studata.admitted_class, term = term, dayboarding = studata.dayboarding)
                    varrid1 = tblbill.objects.filter(klass = studata.admitted_class, term = term, dayboarding = studata.dayboarding).aggregate(Sum('billamount'))
                    varrid = varrid1['billamount__sum']
                    for j in getbill:
                        billdic = {
                            'desc': j.desc,
                            'billamount': locale.format('%.2f', j.billamount, grouping = True) }
                        billlist.append(billdic)

                if tbladditionalbill.objects.filter(session = session, admissionno = studata.admissionno, klass = studata.admitted_class, term = term).count() == 0:
                    varrid2 = 0
                    getaddbill = ''
                else:
                    getaddbill = tbladditionalbill.objects.filter(session = session, admissionno = studata.admissionno, klass = studata.admitted_class, term = term)
                    varrid11 = tbladditionalbill.objects.filter(session = session, admissionno = studata.admissionno, klass = studata.admitted_class, term = term).aggregate(Sum('billamount'))
                    varrid2 = varrid11['billamount__sum']
                    for h in getaddbill:
                        billdic = {
                            'desc': h.desc,
                            'billamount': locale.format('%.2f', h.billamount, grouping = True) }
                        billlist.append(billdic)

                varrid = varrid + varrid2
                billdic = {
                    'student': studata,
                    'bill': billlist,
                    'totalbill': locale.format('%.2f', varrid, grouping = True) }
                bill_list.append(billdic)


                return render_to_response('assessment/billreport.html',{'varuser':varuser, 'varerr':varerr,'bill_list':bill_list,'school':school,'session':session,'term':term,'klass':studata.admitted_class})

        # return render_to_response('bill/printbill.html',{'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')


def mystudykit(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        form= studentform()
        return render_to_response('assessment/mystudykit.html',{'form':form,'varuser':varuser})
    else:
        return HttpResponseRedirect('/login/')

def mycomm(request):
    if 'userid' in request.session:
        varuser=request.session['userid']
        data=Student.objects.get(fullname=varuser,admitted_session=currse,gone=False)
        assignment=tblassignment.objects.filter(session=data.admitted_session,klass=data.admitted_class).order_by('submit_on','id')

        # form= studentform()
        return render_to_response('assignment/assignment.html',{'data':assignment,'varuser':varuser})
    else:
        return HttpResponseRedirect('/login/')


def unautho(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        varerr =''
        return render_to_response('assessment/unautorise.htm',{'varerr':varerr,'varuser':str(varuser).upper()})
    else:
        return HttpResponseRedirect('/login/')







def enterca(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)

        ccc = ClassTeacher.objects.filter(teachername = varuser)
        sss = subjectteacher.objects.filter(teachername = varuser)

        if sss.count() == 0 :
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        sec = ''
        pry = ''
        for j in appused.objects.all():
            pry = j.primary
            sec = j.secondary
        if sec is True :
            pass
        else:
            return HttpResponseRedirect('/reportsheet/access-denied/')
        if request.method == 'POST':
            form = caform(request.POST) # A form bound to the POST data
            if form.is_valid():
                session = form.cleaned_data['session']
                klass = form.cleaned_data['klass']
                term = form.cleaned_data['term']
                arm = form.cleaned_data['arm']
                subject = form.cleaned_data['subject']
                reporttype = form.cleaned_data['reporttype']

                return HttpResponseRedirect('/reportsheet/secondary_print_assessment/%s/%s/%s/%s/%s/%s/'%(str(session).replace('/','j'),str(klass).replace(' ','k'),str(arm).replace(' ','k'),str(subject).replace(' ','k'),str(reporttype).replace(' ','w'),str(term).replace(' ','0')))
        else:
            form = caform()
            if user.createuser==1:
                return render_to_response('assessment/enterca.html',{'varuser':varuser,'form':form,'varerr':varerr})
            elif ccc.count() > 0:
                return render_to_response('assessment/enterca_cl.html',{'varuser':varuser,'form':form,'varerr':varerr})
            elif ccc.count()==0:
                return render_to_response('assessment/enterca_t.html',{'varuser':varuser,'form':form,'varerr':varerr})



    else:
        return HttpResponseRedirect('/login/')


def teacher_report(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        if subjectteacher.objects.filter(teachername = varuser).count() == 0 :
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        sec = ''
        pry = ''
        school=School.objects.get(id =1)
        for j in appused.objects.all():
            pry = j.primary
            sec = j.secondary
        if sec is True :
            pass
        else:
            return HttpResponseRedirect('/reportsheet/access-denied/')
        if request.method == 'POST':
            form = caform(request.POST)
            if form.is_valid():
                session = form.cleaned_data['session']
                klass = form.cleaned_data['klass']
                term = form.cleaned_data['term']
                arm = form.cleaned_data['arm']
                subject = form.cleaned_data['subject']
                stu=Student.objects.filter(admitted_session=session,admitted_class=klass,admitted_arm=arm,gone=False)
                replist=[]
                for j in stu:
                        acadec= StudentAcademicRecord.objects.filter(student=j,term=term)
                        for recf in acadec:
                            rec=SubjectScore.objects.filter(academic_rec=recf,
                                subject=subject)
                            reca={'rec':rec,'stu':j}
                            replist.append(reca)
            return render_to_response('assessment/scoresheet.html',{'varuser':varuser,'school':school,'session':session,'term':term, 'date':date,'form':form,'subject':subject,'class':klass,'replist':replist})
        else:
            form = caform()
        return render_to_response('assessment/scoresheet.html',{'varuser':varuser,'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')



def commentca(request):
    if  "userid" in request.session:
        varuser=request.session['userid']
        if ClassTeacher.objects.filter(teachername = varuser).count() == 0 :
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr=''
        form = cacomform()
        return render_to_response('assessment/entcom.html',{'varuser':varuser,'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')


def stucom(request):  #this needs updating
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                session,klass,arm,term,ca = acccode.split(':')
                #print klass
                data = []



                if term == 'First':
                    getstu = Student.objects.filter(first_term=True, admitted_class = klass,admitted_arm=arm,admitted_session = session,gone = False).order_by('surname')
                elif term == 'Second' :
                    getstu = Student.objects.filter(second_term=True, admitted_class = klass,admitted_arm=arm,admitted_session = session,gone = False).order_by('surname')
                elif term == 'Third':
                    getstu = Student.objects.filter(third_term=True, admitted_class = klass,admitted_arm=arm,admitted_session = session,gone = False).order_by('surname')


                for p in getstu:
                    if StudentAcademicRecord.objects.filter(student = p,term = term):
                        comm = StudentAcademicRecord.objects.get(student = p,term = term)
                        affec = AffectiveSkill.objects.get(academic_rec = comm)
                        psyco = PsychomotorSkill.objects.get(academic_rec = comm)
                        stdic = {'studentinfo':p,'comment':comm,'affective':affec,'psyco':psyco}
                        data.append(stdic)

                if ca=='Mid term':
                    return render_to_response('assessment/comca.html',{'ca':ca,
                    'klass':klass,'data':data,'session':session,'term':term,'arm':arm
                    })

                elif ca=='End term':
                    return render_to_response('assessment/comment.html',{'ca':ca,
                    'klass':klass,'data':data,'session':session,'term':term,'arm':arm
                    })


            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')









def getclass(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                state = acccode
                kk = []
                sdic = {}

                data = subjectteacher.objects.filter(teachername = varuser,status = 'ACTIVE',session = state).order_by('klass')
                for j in data:
                    j = j.klass
                    s = {j:j}
                    sdic.update(s)

                data1= groupteacher.objects.filter(teachername = varuser,status = 'ACTIVE',session = state).order_by('klass')
                for j in data1:
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



def getarm(request):
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
                data = subjectteacher.objects.filter(teachername = varuser,status = 'ACTIVE',session = session,klass = klass).order_by('arm')
                for j in data:
                    j = j.arm
                    #print j
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

def getarmgroup(request):
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
                data = subjectteacher.objects.filter(teachername = varuser,status = 'ACTIVE',session = session,klass = klass).order_by('arm')
                for j in data:
                    j = j.arm
                    #print j
                    s = {j:j}
                    sdic.update(s)

                data1 = groupteacher.objects.filter(teachername = varuser,status = 'ACTIVE',session = session,klass = klass).order_by('group')
                for j in data1:
                    j = j.group
                    #print j
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


def getmyterm(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                state = acccode
                kk = []
                sdic = {}
                data = subjectteacher.objects.filter(teachername = varuser,status = 'ACTIVE',session = state).order_by('term')
                for j in data:
                    j = j.term
                    #print j
                    s = {j:j}
                    sdic.update(s)
                klist = sdic.values()
                klist.sort()
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







def getterm(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                state = acccode
                kk = []
                sdic = {}
                term=tblterm.objects.get(status='ACTIVE')
                term=term.term
                data = subjectteacher.objects.filter(teachername = varuser,status = 'ACTIVE',session = state,term=term)
                for j in data:
                    j = j.term
                    #print j
                    s = {j:j}
                    sdic.update(s)
                klist = sdic.values()
                klist.sort()
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


def getsubject(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                #state = acccode
                #print acccode
                session,klass,arm,term = acccode.split(':')
                kk = []
                sdic = {}
                data = subjectteacher.objects.filter(teachername = varuser,status = 'ACTIVE',session = session,klass = klass,arm = arm)
                for j in data:
                    j = j.subject
                    #print j
                    s = {j:j}
                    sdic.update(s)

                data1 = groupteacher.objects.filter(teachername = varuser,status = 'ACTIVE',session = session,klass = klass,group = arm)
                for j in data1:
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


def getsubjectlesson(request):
    if "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr = ""
                post = request.POST.copy()
                acccode = post['userid']
               # state = acccode
                session,klass = acccode.split(':')
                kk = []
                sdic = {}
                data = subjectteacher.objects.filter(teachername = varuser,session=session,klass = klass)
                for j in data:
                    j = j.subject
                    s = {j:j}
                    sdic.update(s)
                kk = sdic.values()
                sublists=kk
                #klist = sdic.values()
                #for p in klist:
                #    kk.append(p)
                return HttpResponse(json.dumps(kk),mimetype='application/json')
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')


def getstudent(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                session,klass,arm,term, subject,reporttype= acccode.split(':')
                stlist = []

                if term == 'Third':
                    stuk= Student.objects.filter(admitted_session = session,third_term=True,
                        admitted_class = klass,
                        admitted_arm = arm,
                        gone = False)

                    tday = datetime.date.today()
                    if tday.year < 2212:
                        if tblpin.objects.filter(ydate__year = tday.year):
                           gdate = tblpin.objects.get(ydate__year = tday.year)
                           if tday < gdate.ydate:
                              pass
                           else:
                              gpin = gdate.pin
                              gused = gdate.used
                              k = decrypt1(str(gused))
                              uu = encrypt(k)
                              if str(gpin) == str(uu):
                                 pass
                              else:
                                 return HttpResponseRedirect('/sysadmin/page-expire/%s/'%int(tday.year))
                    else:
                         return HttpResponseRedirect('/sysadmin/page-expire/%s/'%int(tday.year))

                if term == 'First':
                    stuk= Student.objects.filter(admitted_session = session,first_term=True,
                        admitted_class = klass,
                        admitted_arm = arm,
                        gone = False)

                elif term=='Second':
                    stuk= Student.objects.filter(admitted_session = session,second_term=True,
                        admitted_class = klass,
                        admitted_arm = arm,
                        gone = False)


                data2 = subjectteacher.objects.filter(teachername=varuser,
                    status = 'ACTIVE',
                    klass=klass,
                    arm=arm,
                    term=term,
                    subject=subject,
                    session = session).count()

                # return render_to_response('assessment/selectloan.html',{'msg':data2})

                if data2 > 0:

                    try:
                        Arm.objects.get(arm=arm)

                        for j in stuk:

                            fd=StudentAcademicRecord.objects.filter(student = j,
                                session = session,
                                klass=j.admitted_class,
                                term = term).count()


                            if fd == 1:

                                st = StudentAcademicRecord.objects.get(student = j,
                                    session = session,
                                    term = term)

                                fnh = SubjectScore.objects.filter(academic_rec = st,
                                    klass = klass,
                                    subject = subject,
                                    session = session,
                                    arm=arm,
                                    term =term).count()

                                if fnh==1:

                                    gs = SubjectScore.objects.get(academic_rec = st,
                                        klass = klass,
                                        subject = subject,
                                        session = session,
                                        arm=arm,term =term)


                                    kk = {'id':gs.id,
                                    'admissionno':j.admissionno,
                                    'fullname':j.fullname,
                                    'sex':j.sex,
                                    'subject':gs.subject,
                                    'term':str(term),
                                    'first_ca':gs.first_ca,
                                    'second_ca':gs.second_ca,
                                    'third_ca':gs.third_ca,
                                    'fourth_ca':gs.fourth_ca,
                                    'fifth_ca':gs.fifth_ca,
                                    'sixth_ca':gs.sixth_ca,
                                    'klass':gs.klass,
                                    'arm':gs.arm,
                                    'exam_score':gs.end_term_score}
                                    stlist.append(kk)


                                # else:
                                #     msg="I am tired"
                                    # return render_to_response('assessment/selectloan.html',{'msg':msg})
                            # else:
                            #     msg ="No such record"
                                # return render_to_response('assessment/selectloan.html',{'msg':msg})

                    except:
                        for j in stuk:

                            fd=StudentAcademicRecord.objects.filter(student = j,
                                session = session,
                                term = term).count()

                            fnh = SubjectScore.objects.filter(academic_rec = st,
                                klass = klass,
                                subject = subject,
                                session = session,
                                subject_group =arm,
                                term =term).count()


                            if fd == 1:

                                st = StudentAcademicRecord.objects.get(student = j,
                                    session = session,
                                    term = term)


                                if fnh==1:

                                    gs = SubjectScore.objects.get(academic_rec = st,
                                        klass = klass,
                                        subject = subject,
                                        session = session,
                                        subject_group=arm,
                                        term =term)


                                    kk = {'id':gs.id,
                                    'admissionno':j.admissionno,
                                    'fullname':j.fullname,
                                    'sex':j.sex,
                                    'subject':gs.subject,
                                    'term':str(term),
                                    'first_ca':gs.first_ca,
                                    'second_ca':gs.second_ca,
                                    'third_ca':gs.third_ca,
                                    'fourth_ca':gs.fourth_ca,
                                    'fifth_ca':gs.fifth_ca,
                                    'sixth_ca':gs.sixth_ca,
                                    'klass':gs.klass,
                                    'arm':gs.arm,
                                    'exam_score':gs.end_term_score}
                                    stlist.append(kk)
                                else:
                                    pass
                    if reporttype=='Mid term':
                        # if klass=='JS 1' or klass== 'SS 1':
                        return render_to_response('assessment/mid.html',{'data':stlist,'subject':subject,'term':term,'klass':klass,'arm':arm,'report':reporttype})
                        # else:
                        #     return render_to_response('assessment/ca_first.html',{'data':stlist})
                    elif reporttype=='End term':
                        # if klass=='JS 1' or klass== 'SS 1':
                        return render_to_response('assessment/endterm.html',{'data':stlist,'subject':subject,'term':term,'klass':klass,'arm':arm,'report':reporttype})
                        # else:
                        #     return render_to_response('assessment/ca_first.html',{'data':stlist})

                else:
                    varerr='User not asigned for the term'
                    return render_to_response('assessment/notallowed.html',{'varerr':varerr})

            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def getstudent__old(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                session,klass,arm,term, subject,reporttype= acccode.split(':')
                stlist = []

                if term == 'Third':
                    stuk= Student.objects.filter(admitted_session = session,third_term=True,
                        admitted_class = klass,
                        admitted_arm = arm,
                        gone = False)

                    tday = datetime.date.today()
                    if tday.year < 2212:
                        if tblpin.objects.filter(ydate__year = tday.year):
                           gdate = tblpin.objects.get(ydate__year = tday.year)
                           if tday < gdate.ydate:
                              pass
                           else:
                              gpin = gdate.pin
                              gused = gdate.used
                              k = decrypt1(str(gused))
                              uu = encrypt(k)
                              if str(gpin) == str(uu):
                                 pass
                              else:
                                 return HttpResponseRedirect('/sysadmin/page-expire/%s/'%int(tday.year))
                    else:
                         return HttpResponseRedirect('/sysadmin/page-expire/%s/'%int(tday.year))
                else:
                    pass

                data2 = subjectteacher.objects.filter(teachername=varuser,
                    status = 'ACTIVE',
                    klass=klass,
                    arm=arm,
                    term=term,
                    subject=subject,
                    session = session).count()

                if term == 'First':
                    stuk= Student.objects.filter(admitted_session = session,first_term=True,
                        admitted_class = klass,
                        admitted_arm = arm,
                        gone = False)

                elif term=='Second':
                    stuk= Student.objects.filter(admitted_session = session,second_term=True,
                        admitted_class = klass,
                        admitted_arm = arm,
                        gone = False)

                # msg = data2
                # return render_to_response('assessment/selectloan.html',{'msg':data2})


                if data2 > 0:

                    try:
                        Arm.objects.get(arm=arm)

                        for j in stuk:


                            if StudentAcademicRecord.objects.filter(student = j,session = session,term = term):

                                st = StudentAcademicRecord.objects.get(student = j,session = session,term = term)

                                if SubjectScore.objects.filter(academic_rec = st,klass = klass,subject = subject,session = session,arm=arm,term =term):

                                    gs = SubjectScore.objects.get(academic_rec = st,klass = klass,subject = subject,session = session,arm=arm,term =term)

                                    kk = {'id':gs.id,
                                    'admissionno':j.admissionno,
                                    'fullname':j.fullname,
                                    'sex':j.sex,
                                    'subject':gs.subject,
                                    'term':str(term),
                                    'first_ca':gs.first_ca,
                                    'second_ca':gs.second_ca,
                                    'third_ca':gs.third_ca,
                                    'fourth_ca':gs.fourth_ca,
                                    'fifth_ca':gs.fifth_ca,
                                    'sixth_ca':gs.sixth_ca,
                                    'klass':gs.klass,
                                    'arm':gs.arm,
                                    'exam_score':gs.end_term_score}
                                    stlist.append(kk)
                                else:
                                    pass
                    except:
                        for j in Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False):
                            if StudentAcademicRecord.objects.filter(student = j,session = session,term = term):
                                st = StudentAcademicRecord.objects.get(student = j,session = session,term = term)
                                if SubjectScore.objects.filter(academic_rec = st,klass = klass,subject = subject,session = session,subject_group=arm,term =term):
                                    gs = SubjectScore.objects.get(academic_rec = st,klass = klass,subject = subject,session = session,subject_group=arm,term =term)
                                    kk = {'id':gs.id,
                                    'admissionno':j.admissionno,
                                    'fullname':j.fullname,
                                    'sex':j.sex,
                                    'subject':gs.subject,
                                    'term':str(term),
                                    'first_ca':gs.first_ca,
                                    'second_ca':gs.second_ca,
                                    'third_ca':gs.third_ca,
                                    'fourth_ca':gs.fourth_ca,
                                    'fifth_ca':gs.fifth_ca,
                                    'sixth_ca':gs.sixth_ca,
                                    'klass':gs.klass,
                                    'arm':gs.arm,
                                    'exam_score':gs.end_term_score}
                                    stlist.append(kk)
                                else:
                                    pass
                    if reporttype=='Mid term':
                        # if klass=='JS 1' or klass== 'SS 1':
                        return render_to_response('assessment/mid.html',{'data':stlist,'subject':subject,'term':term,'klass':klass,'arm':arm,'report':reporttype})
                        # else:
                        #     return render_to_response('assessment/ca_first.html',{'data':stlist})
                    elif reporttype=='End term':
                        # if klass=='JS 1' or klass== 'SS 1':
                        return render_to_response('assessment/endterm.html',{'data':stlist,'subject':subject,'term':term,'klass':klass,'arm':arm,'report':reporttype})
                        # else:
                        #     return render_to_response('assessment/ca_first.html',{'data':stlist})

                else:
                    varerr='User not asigned'
                    return render_to_response('assessment/notallowed.html',{'varerr':varerr})

            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')


def getassign(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                state=acccode
                session,klass,arm,term, subject= acccode.split(':')
                myassign=tblassignment.objects.filter(teacher=varuser,session=session,term=term,klass=klass,arm=arm,subject=subject)
                return HttpResponse(json.dumps(kk), mimetype='application/json')
                # return render_to_response('assignment/tview.html',{'data':myassign})

    else:
        return HttpResponseRedirect('/login/')



def editca(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.staffname
        sec = ''
        pry = ''
        for j in appused.objects.all():
            pry = j.primary
            sec = j.secondary
        if sec is True :
            pass
        else:
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails = SubjectScore.objects.get(id = vid)
        admno1 = getdetails.academic_rec.student.admissionno
        klass1 = getdetails.klass
        arm1 = getdetails.arm
        subject1 = getdetails.subject
        session1 = getdetails.session
        term1 = getdetails.term
        if request.method == 'POST':
             ca1 = request.POST['firstca']
             ca2 = request.POST['secondca']
             ca3 = request.POST['thirdca']
             ca4 = request.POST['fourthca']
             exam = request.POST['exam']
             if exam == "":
                 exam = 0
             if ca1 == "":
                 ca1 = 0
             if ca2 == "":
                 ca2 = 0
             if ca3 == "":
                 ca3 = 0
             if ca4 == "":
                 ca4 = 0
             try:
                h = int(exam)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             try:
                 h1 = int(ca1)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             try:
                 h2 = int(ca2)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             try:
                 h3 = int(ca3)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             try:
                 h4 = int(ca4)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             if klass1 =='SS 3' and term1 =='Second':
                 h1 = 0
                 h2 = 0
                 h3 = 0
             elif klass1 =='JS 3' and term1 =='Second':
                 h1 = 0
                 h2 = 0
                 h3 = 0
             else:
                 if h > 70 :
                     h = 0
                 if h1 > 10 :
                     h1 = 0
                 if h2 > 10 :
                     h2 = 0
                 if h3 > 10 :
                     h3 = 0
                 if h4 > 10 :
                     h4 = 0
             getdetails.first_ca = h1
             getdetails.second_ca = h2
             getdetails.third_ca = h3
             getdetails.fourth_ca = h4
        #     getdetails.sixth_ca = h3
        #     getdetails.fifth_ca = h1+h2
             getdetails.exam_score = h
             getdetails.save()
             #**********************getting the class average
             getdetails2 = SubjectScore.objects.get(id = vid)
             admno = getdetails2.academic_rec.student.admissionno
             klass = getdetails2.klass
             arm = getdetails2.arm
             subject = getdetails2.subject
             session = getdetails2.session
             term = getdetails2.term
             fullname = getdetails2.academic_rec.student.fullname

             #************TOTTAL STUDENT IN CLASS offering subject************
             totstudent = SubjectScore.objects.filter(session = session,term = term,klass = klass,arm = arm,subject = subject).count()
             #********************term score total****************
             totsubject = SubjectScore.objects.filter(session = session,term = term,klass = klass,arm = arm,subject = subject).aggregate(Sum('end_term_score'))

             varrid = totsubject['end_term_score__sum']
             subavg = varrid/totstudent
             annavg = 0
             if term == 'Third':
                 an = annualaverage(str(admno),str(session),str(arm),str(klass),str(subject))
             SubjectScore.objects.filter(klass = klass,arm = arm,subject = subject,session = session,term = term).update(subject_teacher = uenter.upper(),subject_avg = subavg)
             #***************************getting subject position**************************#
             sp = subjectposition(str(session),str(subject),str(term),str(klass),str(arm))
             #*****************************calculate percentage
             tn = percent(str(session),str(klass),str(arm),str(admno),str(term))
             #***********************getting the class position
             cp = classposition(str(session),str(term),str(klass),str(arm))
             #************getting stream position****************
             cp1 = classposition1(str(session),str(term),str(klass))
             c = klass[0] #if the first alphabet of thee selected class is P FOR PRIMMARY, Y FOR YEAR, B FOR BASIC , N FOR NURSERY C FOR CLASS, L FOR LOWER PRIMARY
             if c.upper() =='P' or c.upper() == 'Y' or c.upper() == 'B' or c.upper() == 'N' or c.upper() == 'C' or c.upper() == 'L':
                 return HttpResponseRedirect('/reportsheet/primary_assessment/%s/%s/%s/%s/%s/'%(str(session).replace('/','j'),str(klass).replace(' ','k'),str(arm).replace(' ','k'),str(fullname).replace(' ','z'),str(term).replace(' ','0')))
             else:  #for JSS AND SSS
                 #return HttpResponseRedirect('/reportsheet/enterca/')
                 return HttpResponseRedirect('/reportsheet/secondary_assessment/%s/%s/%s/%s/%s/'%(str(session).replace('/','j'),str(klass).replace(' ','k'),str(arm).replace(' ','k'),str(subject).replace(' ','z'),str(term).replace(' ','0')))
        else:
            form = caform()
            return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')



def editcas(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.staffname
        sec = ''
        pry = ''
        for j in appused.objects.all():
            pry = j.primary
            sec = j.secondary
        if sec is True :
            pass
        else:
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails = SubjectScore.objects.get(id = vid)
        admno1 = getdetails.academic_rec.student.admissionno
        klass1 = getdetails.klass
        arm1 = getdetails.arm
        subject1 = getdetails.subject
        session1 = getdetails.session
        term1 = getdetails.term

        if request.method == 'POST':
             ca4 = request.POST['fourthca']
             ca5 = request.POST['fifthca']
             ca6 = request.POST['sixthca']
             rep = request.POST['report']


             if ca4 == "":
                 ca4 = 0
             if ca5 == "":
                 ca5 = 0
             if ca6 == "":
                 ca6 = 0

             h4 = int(ca4)
             h5 = int(ca5)
             h6 = int(ca6)


             if h4 > 20 :
                 h4 = 0
             if h5 > 20 :
                 h5 = 0
             if h6 > 60 :
                 h6 = 0

             getdetails.fourth_ca = h4
             getdetails.fifth_ca = h5
             getdetails.sixth_ca = h6

             getdetails.save()

             #**********************getting the classroom average*********************
             getdetails2 = SubjectScore.objects.get(id = vid)
             admno = getdetails2.academic_rec.student.admissionno
             klass = getdetails2.klass
             arm = getdetails2.arm
             grp=getdetails2.subject_group
             subject = getdetails2.subject
             session = getdetails2.session
             term = getdetails2.term
             fullname = getdetails2.academic_rec.student.fullname




             #************TOTAL STUDENT IN CLASS offering subject************
             totstudent = SubjectScore.objects.filter(session = session,term = term,klass = klass,arm = arm,subject = subject).count()


             #********************endterm score total****************
             totsubject = SubjectScore.objects.filter(session = session,term = term,klass = klass,arm = arm,subject = subject).aggregate(Sum('end_term_score'))
             varrid = totsubject['end_term_score__sum']

             subavg = varrid/totstudent

             SubjectScore.objects.filter(klass = klass,arm = arm,subject = subject,session = session,term = term).update(subject_teacher = uenter.upper(),subject_avg = subavg)

             annavg = 0
             if term == 'Third':
                 an = annualaverage(str(admno),str(session),str(arm),str(klass),str(subject))



             #***************************getting subject position**************************#
             sp = subjectposition(str(session),str(subject),str(term),str(klass),str(arm))


             #*****************************calculate percentage
             # tn = percent(str(session),str(klass),str(arm),str(admno),str(term))


             #******************getting mid term classroom average*****************
             ca=classaverageEnd(klass,session,term,arm)

             sa=studentaverageEnd(admno,term,session,klass,arm)



             #***********************getting the classroom position*******
             cp = classposition(str(session),str(term),str(klass),str(arm))


             #************getting class position****************
             cp1 = classposition1(str(session),str(term),str(klass))
             c = klass[0]

             return HttpResponseRedirect('/reportsheet/secondary_assessment/%s/%s/%s/%s/%s/%s/%s/'%(str(session).replace('/','j'),str(klass).replace(' ','k'),str(arm).replace(' ','k'),str(subject).replace(' ','k'),str(term).replace(' ','0'),str(grp).replace(' ','m'),str(rep).replace(' ','p')))


        else:
            form = caform()
            return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')


def editcas_ori(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.staffname
        sec = ''
        pry = ''
        for j in appused.objects.all():
            pry = j.primary
            sec = j.secondary
        if sec is True :
            pass
        else:
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails = SubjectScore.objects.get(id = vid)
        admno1 = getdetails.academic_rec.student.admissionno
        klass1 = getdetails.klass
        arm1 = getdetails.arm
        subject1 = getdetails.subject
        session1 = getdetails.session
        term1 = getdetails.term

        if request.method == 'POST':
             ca4 = request.POST['fourthca']
             ca5 = request.POST['fifthca']
             ca6 = request.POST['sixthca']
             rep = request.POST['report']

             if ca4 == "":
                 ca4 = 0
             if ca5 == "":
                 ca5 = 0
             if ca6 == "":
                 ca6 = 0



             h4 = int(ca4)
             h5 = int(ca5)
             h6 = int(ca6)

             if klass1 =='SS 3' and term1 =='Second':
                 h1 = 0
                 h2 = 0
             elif klass1 =='JS 3' and term1 =='Second':
                 h1 = 0
                 h2 = 0
             else:

                 if h4 > 20 :
                     h4 = 0
                 if h5 > 20 :
                     h5 = 0
                 if h6 > 60 :
                     h6 = 0

             getdetails.fourth_ca = h4
             getdetails.fifth_ca = h5
             getdetails.sixth_ca = h6
             getdetails.save()

             #**********************getting the classroom average*********************
             getdetails2 = SubjectScore.objects.get(id = vid)
             admno = getdetails2.academic_rec.student.admissionno
             klass = getdetails2.klass
             arm = getdetails2.arm
             grp=getdetails2.subject_group
             subject = getdetails2.subject
             session = getdetails2.session
             term = getdetails2.term
             fullname = getdetails2.academic_rec.student.fullname


             #************TOTAL STUDENT IN CLASS offering subject************
             totstudent = SubjectScore.objects.filter(session = session,term = term,klass = klass,arm = arm,subject = subject).count()


             #********************term score total****************
             totsubject = SubjectScore.objects.filter(session = session,term = term,klass = klass,arm = arm,subject = subject).aggregate(Sum('end_term_score'))
             varrid = totsubject['end_term_score__sum']
             subavg = varrid/totstudent
             SubjectScore.objects.filter(klass = klass,arm = arm,subject = subject,session = session,term = term).update(subject_teacher = uenter.upper(),subject_avg = subavg)

             annavg = 0
             if term == 'Third':
                 an = annualaverage(str(admno),str(session),str(arm),str(klass),str(subject))



             #***************************getting subject position**************************#
             sp = subjectposition(str(session),str(subject),str(term),str(klass),str(arm))


             #*****************************calculate percentage
             # tn = percent(str(session),str(klass),str(arm),str(admno),str(term))


             #******************getting mid term classroom average*****************
             ca=classaverageEnd(klass,session,term,arm)

             sa=studentaverageEnd(admno,term,session,klass,arm)



             #***********************getting the classroom position*******
             cp = classposition(str(session),str(term),str(klass),str(arm))


             #************getting class position****************
             cp1 = classposition1(str(session),str(term),str(klass))
             c = klass[0]

             return HttpResponseRedirect('/reportsheet/secondary_assessment/%s/%s/%s/%s/%s/%s/%s/'%(str(session).replace('/','j'),str(klass).replace(' ','k'),str(arm).replace(' ','k'),str(subject).replace(' ','k'),str(term).replace(' ','0'),str(grp).replace(' ','m'),str(rep).replace(' ','p')))


        else:
            form = caform()
            return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')


def editcas2bothtypes(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.staffname



        varerr =''
        getdetails = SubjectScore.objects.get(id = vid)
        admno1 = getdetails.academic_rec.student.admissionno
        klass1 = getdetails.klass
        arm1 = getdetails.arm
        subject1 = getdetails.subject
        session1 = getdetails.session
        term1 = getdetails.term
        grp=getdetails.subject_group

        if request.method == 'POST':
             ca1 = request.POST['firstca']
             ca2 = request.POST['secondca']
             ca3 = request.POST['thirdca']

             ca4 = request.POST['fourthca']
             ca5 = request.POST['fifthca']
             ca6 = request.POST['sixthca']
             rep = request.POST['report']



             ca1= int(ca1)
             ca2 = int(ca2)
             ca3 = int(ca3)


             ca4 = int(ca4)
             ca5 = int(ca5)
             ca6 = int(ca6)

             # msg = h3,h4,h6
             # return render_to_response('assessment/selectloan.html',{'msg':msg})

             if ca1 == "":
                 ca1 = 0
             if ca2 == "":
                 ca2 = 0
             if ca3 == "":
                 ca3 = 0


             if ca4 == "":
                 ca4 = 0
             if ca5 == "":
                 ca5 = 0
             if ca6 == "":
                 ca6 = 0



             if klass1 =='SS 3' and term1 =='Second':
                 ca1 = 0
                 ca2 = 0
             elif klass1 =='JS 3' and term1 =='Second':
                 ca1 = 0
                 ca2 = 0



             if ca1 > 10 :
                 ca1 = 0

             if ca2 > 10 : #obj cbt mid term
                 ca2 = 0

             if ca3> 20 : #theory mid term
                 ca3 = 0


             if ca4 > 20 : #ca end term
                 ca4 = 0

             if ca5 > 20 : #obj cbt end term
                 ca5 = 0
             if ca6 > 60 : #theory end term
                 ca6 = 0


             getdetails.first_ca = ca1
             getdetails.second_ca = ca2

             getdetails.third_ca = ca3


             getdetails.fourth_ca = ca4

             getdetails.fifth_ca = ca5
             getdetails.sixth_ca = ca6

             getdetails.save()



    #          # I WISH THE CODE ENDS HERE, SO TECHERS SPEND JUST SECONDS ENTERING SCORES

             dddt = datetime.datetime.now()

             mytime = dddt.time()


             pp = tblrunp.objects.filter(session = session1,
                klass=klass1,
                term=term1,
                arm=arm1,
                reportsheet=rep)

             pp_count= pp.count()

             if pp_count==1:
                pp = pp.get(term=term1)

                pp.subject=subject1
                pp.time=mytime
                pp.status=1
                pp.save()

             elif pp_count==0:

                tblrunp(session = session1,
                    subject=subject1,
                    time=mytime,
                    klass=klass1,
                    status=1,
                    term=term1,
                    arm=arm1, reportsheet=rep).save()


             return HttpResponseRedirect('/reportsheet/secondary_assessment/%s/%s/%s/%s/%s/%s/%s/'%(str(session1).replace('/','j'),str(klass1).replace(' ','k'),str(arm1).replace(' ','k'),str(subject1).replace(' ','k'),str(term1).replace(' ','0'),str(grp).replace(' ','m'),str(rep).replace(' ','p')))


             c = klass1[0]

             return HttpResponseRedirect('/reportsheet/secondary_assessment/%s/%s/%s/%s/%s/%s/%s/'%(str(session1).replace('/','j'),str(klass1).replace(' ','k'),str(arm1).replace(' ','k'),str(subject1).replace(' ','k'),str(term1).replace(' ','0'),str(grp).replace(' ','m'),str(rep).replace(' ','p')))


        else:
            form = caform()
            return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')

def editcas2(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.staffname
        sec = ''
        pry = ''
        for j in appused.objects.all():
            pry = j.primary
            sec = j.secondary

        if sec is False :
            return HttpResponseRedirect('/reportsheet/access-denied/')


        varerr =''
        getdetails = SubjectScore.objects.get(id = vid)
        admno1 = getdetails.academic_rec.student.admissionno
        klass1 = getdetails.klass
        arm1 = getdetails.arm
        subject1 = getdetails.subject
        session1 = getdetails.session
        term1 = getdetails.term
        grp=getdetails.subject_group

        if request.method == 'POST':
             ca1 = request.POST['firstca']
             ca2 = request.POST['secondca']
             ca3 = request.POST['thirdca']
             rep = request.POST['report']

             if ca1 == "":
                 ca1 = 0
             if ca2 == "":
                 ca2 = 0
             if ca3 == "":
                 ca3 = 0

             h1= int(ca1)
             h2 = int(ca2)
             h3 = int(ca3)


             if klass1 =='SS 3' and term1 =='Second':
                 h1 = 0
                 h2 = 0
             elif klass1 =='JS 3' and term1 =='Second':
                 h1 = 0
                 h2 = 0
             else:
                 if h1 > 10 :
                     h1 = 0
                 if h2 > 10 :
                     h2 = 0
                 if h3> 20 :
                     h3 = 0

             getdetails.first_ca = h1
             getdetails.second_ca = h2
             getdetails.third_ca = h3

             getdetails.save()

             # I WISH THE CODE ENDS HERE, SO TECHERS SPEND JUST SECONDS ENTERING SCORES

    #s**********************midterm Student average*********************
            # if subject1 == 'MATHEMATICS' :
             sa=studentaveragemid(admno1,term1,session1,klass1,arm1) #student stat

             sub=subjectaveragemid(term1,session1,klass1,arm1,subject1) #class stat

          ##*****************midterm classroom average *************************
             ca=classaveragemid(klass1,session1,term1,arm1)#class stat

             return HttpResponseRedirect('/reportsheet/secondary_assessment/%s/%s/%s/%s/%s/%s/%s/'%(str(session1).replace('/','j'),str(klass1).replace(' ','k'),str(arm1).replace(' ','k'),str(subject1).replace(' ','k'),str(term1).replace(' ','0'),str(grp).replace(' ','m'),str(rep).replace(' ','p')))


        else:
            form = caform()
            return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')





def editcapry(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.staffname
        sec = ''
        pry = ''
        for j in appused.objects.all():
            pry = j.primary
            sec = j.secondary
        if pry is True :
            pass
        else:
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails = SubjectScore.objects.get(id = vid)
        admno1 = getdetails.academic_rec.student.admissionno
        klass1 = getdetails.klass
        arm1 = getdetails.arm
        subject1 = getdetails.subject
        session1 = getdetails.session
        term1 = getdetails.term
        if request.method == 'POST':
             ca1 = request.POST['firstca']
             ca2 = request.POST['secondca']
             ca3 = request.POST['thirdca']
             exam = request.POST['exam']
             if exam == "":
                 exam = 0
             if ca1 == "":
                 ca1 = 0
             if ca2 == "":
                 ca2 = 0
             if ca3 == "":
                 ca3 = 0
             try:
                h = int(exam)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             try:
                 h1 = int(ca1)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             try:
                 h2 = int(ca2)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             try:
                 h3 = int(ca3)
             except :
                 return HttpRsponseRedirect('/reportsheet/enterca/')
             if klass1 =='SS 3' and term1 =='Second':
                 h1 = 0
                 h2 = 0
                 h3 = 0
             elif klass1 =='JS 3' and term1 =='Second':
                 h1 = 0
                 h2 = 0
                 h3 = 0
             else:
                 if h > 70 :
                     h = 0
                 if h1 > 10 :
                     h1 = 0
                 if h2 > 10 :
                     h2 = 0
                 if h3 > 10 :
                     h3 = 0
             getdetails.first_ca = h1
             getdetails.second_ca = h2
             getdetails.third_ca = h3
             getdetails.sixth_ca = h3
             getdetails.fifth_ca = h1+h2
             getdetails.exam_score = h
             getdetails.save()
             #**********************getting the class average
             getdetails2 = SubjectScore.objects.get(id = vid)
             admno = getdetails2.academic_rec.student.admissionno
             klass = getdetails2.klass
             arm = getdetails2.arm
             subject = getdetails2.subject
             session = getdetails2.session
             term = getdetails2.term
             fullname = getdetails2.academic_rec.student.fullname
             #************TOTTAL STUDENT IN CLASS offering subject************
             totstudent = SubjectScore.objects.filter(session = session,term = term,klass = klass,arm = arm,subject = subject).count()
             #********************term score total****************
             totsubject = SubjectScore.objects.filter(session = session,term = term,klass = klass,arm = arm,subject = subject).aggregate(Sum('end_term_score'))
             varrid = totsubject['end_term_score__sum']
             subavg = varrid/totstudent
             annavg = 0
             if term == 'Third':
                 an = annualaverage(str(admno),str(session),str(arm),str(klass),str(subject))
             SubjectScore.objects.filter(klass = klass,arm = arm,subject = subject,session = session,term = term).update(subject_teacher = uenter.upper(),subject_avg = subavg)
             #***************************getting subject position**************************#
             sp = subjectposition(str(session),str(subject),str(term),str(klass),str(arm))
             #*****************************calculate percentage
             tn = percent(str(session),str(klass),str(arm),str(admno),str(term))
             #***********************getting the class position
             cp = classposition(str(session),str(term),str(klass),str(arm))
             #************getting stream position****************
             cp1 = classposition1(str(session),str(term),str(klass))
             c = klass[0] #if the first alphabet of thee selected class is P FOR PRIMMARY, Y FOR YEAR, B FOR BASIC , N FOR NURSERY C FOR CLASS, L FOR LOWER PRIMARY
             if c.upper() =='P' or c.upper() == 'Y' or c.upper() == 'B' or c.upper() == 'N' or c.upper() == 'C' or c.upper() == 'L':
                 return HttpResponseRedirect('/reportsheet/primary_assessment/%s/%s/%s/%s/%s/'%(str(session).replace('/','j'),str(klass).replace(' ','k'),str(arm).replace(' ','k'),str(fullname).replace(' ','z'),str(term).replace(' ','0')))
             else:  #for JSS AND SSS
                 #return HttpResponseRedirect('/reportsheet/enterca/')
                 return HttpResponseRedirect('/reportsheet/secondary_assessment/%s/%s/%s/%s/%s/'%(str(session).replace('/','j'),str(klass).replace(' ','k'),str(arm).replace(' ','k'),str(subject).replace(' ','z'),str(term).replace(' ','0')))
        else:
            form = caform()
            return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')


"""
def editca(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.staffname
        sec = ''
        pry = ''
        for j in appused.objects.all():
            pry = j.primary
            sec = j.secondary
        #if pry is True :
        #    pass
        #else:
        #    return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails = SubjectScore.objects.get(id = vid)
        if request.method == 'POST':
             ca1 = request.POST['firstca']
             ca2 = request.POST['secondca']
             ca3 = request.POST['thirdca']
             exam = request.POST['exam']
             if exam == "":
                 exam = 0
             if ca1 == "":
                 ca1 = 0
             if ca2 == "":
                 ca2 = 0
             if ca3 == "":
                 ca3 = 0
             try:
                h = float(exam)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             try:
                 h1 = float(ca1)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             try:
                 h2 = float(ca2)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             try:
                 h3 = float(ca3)
             except :
                 return HttpResponseRedirect('/reportsheet/enterca/')
             if h > 70 :
                 h = 70
             if h1 > 10 :
                 h1 = 10
             if h2 > 10 :
                 h2 = 10
             if h3 > 10 :
                 h3 = 10
             getdetails.first_ca = str(h1)
             getdetails.second_ca = str(h2)
             getdetails.third_ca = str(h3)
             getdetails.exam_score = str(h)
             getdetails.fifth_ca = str(h2)+str(h1)
             getdetails.save()
             #**********************getting the class average
             getdetails2 = SubjectScore.objects.get(id = vid)
             admno = getdetails2.academic_rec.student.admissionno
             klass = getdetails2.klass
             arm = getdetails2.arm
             subject = getdetails2.subject
             session = getdetails2.session
             term = getdetails2.term
             fullname = getdetails2.academic_rec.student.fullname
             totstudent = SubjectScore.objects.filter(klass = klass,arm = arm,subject = subject,session = session,term = term).count()
             totsubject = SubjectScore.objects.filter(klass = klass,arm = arm,subject = subject,session = session,term = term).aggregate(Sum('end_term_score'))
             varrid = totsubject['end_term_score__sum']
             subavg = varrid/totstudent
             annavg = 0
             ns1 = str(subject).replace(' ','z')
             ns = str(ns1).replace('$','q')
             if term == 'Third':
                 an = annualaverage(str(admno),str(session),str(arm),str(klass),str(subject))
                 #print 'Annual Average :',an
             SubjectScore.objects.filter(klass = klass,arm = arm,subject = subject,session = session,term = term).update(subject_teacher = uenter.upper(),subject_avg = subavg)

             #*************************************************************************getting subject position
             sp = subjectposition(str(session),str(subject),str(term),str(klass),str(arm))
             #*****************************calculate percentage
             tn = percent(str(session),str(klass),str(arm),str(admno),str(term))
             #***********************getting the class position
             cp = classposition(str(session),str(term),str(klass),str(arm))
             c = klass[0]
             if c.upper() =='P' or c.upper() == 'Y' or c.upper() == 'B' or c.upper() == 'N' or c.upper() == 'C' or c.upper() == 'L':
                #here i redirect to primary page
                 #return primary_url(str(session),str(klass),str(arm),str(fullname),str(term))
                 fname1 = str(fullname).replace(' ','z')
                 fname2 = fname1.replace('-','i')
                 fname  = fname2.replace("'",'u')
                 return HttpResponseRedirect('/reportsheet/primary_assessment/%s/%s/%s/%s/%s/'%(str(session).replace('/','j'),str(klass).replace(' ','k'),str(arm).replace(' ','k'),fname,str(term).replace(' ','0')))
             else:
                 #return HttpResponseRedirect('/reportsheet/enterca/')
                 return HttpResponseRedirect('/reportsheet/secondary_assessment/%s/%s/%s/%s/%s/'%(str(session).replace('/','j'),str(klass).replace(' ','k'),str(arm).replace(' ','k'),ns,str(term).replace(' ','0')))
        else:
            form = caform()
            return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')
"""

def getsubjectscore(request):
        if  "userid" in request.session:
            if request.is_ajax():
                if request.method == 'POST':
                    varuser = request.session['userid']
                    varerr =""
                    post = request.POST.copy()
                    acccode = post['userid']
                    getdetails = SubjectScore.objects.get(id = acccode)
                    return render_to_response('assessment/editca.html',{'getdetails':getdetails})
                else:
                    gdata = ""
                    return render_to_response('index.html',{'gdata':gdata})
            else:

                gdata = ""
                return render_to_response('getlg.htm',{'gdata':gdata})
        else:
            return HttpResponseRedirect('/login/')

def getsubjectscore1(request):
        if  "userid" in request.session:
            if request.is_ajax():
                if request.method == 'POST':
                    varuser = request.session['userid']
                    varerr =""
                    post = request.POST.copy()
                    acccode = post['userid']
                    vid,acccode= acccode.split(':')
                    getdetails = SubjectScore.objects.get(id = vid)

                    dent = tblde.objects.get(id=1)

                    if dent.status == 1:

                        if acccode=='End term':
                            return render_to_response('assessment/edit_endterm_ca.html',{'getdetails':getdetails,'ak':acccode})

                        elif acccode=='Mid term':
                            return render_to_response('assessment/edit_midterm_ca.html',{'getdetails':getdetails,'ak':acccode})

                    else :
                        return render_to_response('assessment/noedit.html')


                else:
                    gdata = ""
                    return render_to_response('index.html',{'gdata':gdata})
            else:

                gdata = ""
                return render_to_response('getlg.htm',{'gdata':gdata})
        else:
            return HttpResponseRedirect('/login/')


def getsubjectscore2(request):
        if  "userid" in request.session:
            if request.is_ajax():
                if request.method == 'POST':
                    varuser = request.session['userid']
                    varerr =""
                    post = request.POST.copy()
                    acccode = post['userid']

                    # svid,reporttype= acccode.split(':')
                    getdetails = SubjectScore.objects.get(id = acccode)
                    return render_to_response('assessment/editca1.html',{'getdetails':getdetails,'ak':acccode})
                else:
                    gdata = ""
                    return render_to_response('index.html',{'gdata':gdata})
            else:

                gdata = ""
                return render_to_response('getlg.htm',{'gdata':gdata})
        else:
            return HttpResponseRedirect('/login/')

def getsubjectscorep(request):
        if  "userid" in request.session:
            if request.is_ajax():
                if request.method == 'POST':
                    varuser = request.session['userid']
                    varerr =""
                    post = request.POST.copy()
                    acccode = post['userid']
                    getdetails = SubjectScore.objects.get(id = acccode)
                    return render_to_response('assessment/editcap.html',{'getdetails':getdetails})
                else:
                    gdata = ""
                    return render_to_response('index.html',{'gdata':gdata})
            else:

                gdata = ""
                return render_to_response('getlg.htm',{'gdata':gdata})
        else:
            return HttpResponseRedirect('/login/')


def affectivedomain(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        if ClassTeacher.objects.filter(teachername = varuser).count() == 0 :
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails =''
        form = caform()
        return render_to_response('assessment/affective.html',{'varuser':varuser,'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')

def getcomm(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        if ClassTeacher.objects.filter(teachername = varuser).count() == 0 :
            return HttpResponseRedirect('/reportsheet/access-denied/')
        user = userprofile.objects.get(username = varuser)
        varerr =''
        getdetails =''
        form = caform()
        return render_to_response('assessment/comm.html',{'varuser':varuser,'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')

def getclassaff(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                state = acccode
                kk = []
                sdic = {}
                data = ClassTeacher.objects.filter(teachername = varuser,session = state).order_by('klass')
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

def getarmaff(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                state,klass = acccode.split(':')
                kk = []
                sdic = {}
                data = ClassTeacher.objects.filter(teachername = varuser,session = state,klass=klass).order_by('arm')
                for j in data:
                    j = j.arm
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

def getstudentaff(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                session,klass,arm,term = acccode.split(':')
                #print klass
                data = []
                if term == 'First':
                    getstu = Student.objects.filter(first_term = True, admitted_class = klass,admitted_arm=arm,admitted_session = session,gone = False).order_by('-sex','fullname')
                elif term   == 'Second':
                    getstu = Student.objects.filter(second_term = True,admitted_class = klass,admitted_arm=arm,admitted_session = session,gone = False).order_by('-sex','fullname')
                elif term == 'Third' :
                    getstu = Student.objects.filter(third_term = True,admitted_class = klass,admitted_arm=arm,admitted_session = session,gone = False).order_by('-sex','fullname')

                for p in getstu:
                    if StudentAcademicRecord.objects.filter(student = p,term = term):
                        comm = StudentAcademicRecord.objects.get(student = p,term = term)
                        affec = AffectiveSkill.objects.get(academic_rec = comm)
                        psyco = PsychomotorSkill.objects.get(academic_rec = comm)
                        stdic = {'studentinfo':p,'comment':comm,'affective':affec,'psyco':psyco}
                        data.append(stdic)
                return render_to_response('assessment/affec.html',{'klass':klass,
                    'data':data,'session':session,'term':term,'arm':arm})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def comment(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                session,klass,arm,term = acccode.split(':')
                #print klass
                data = []
                getstu = Student.objects.filter(admitted_class = klass,admitted_arm=arm,admitted_session = session,gone = False).order_by('-sex','fullname')
                for p in getstu:
                    if StudentAcademicRecord.objects.filter(student = p,term = term):
                        comm = StudentAcademicRecord.objects.get(student = p,term = term)
                        affec = AffectiveSkill.objects.get(academic_rec = comm)
                        psyco = PsychomotorSkill.objects.get(academic_rec = comm)
                        stdic = {'studentinfo':p,'comment':comm,'affective':affec,'psyco':psyco}
                        data.append(stdic)
                return render_to_response('assessment/comment.html',{'data':data})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def getaffective(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                getdetails = AffectiveSkill.objects.get(id = acccode)
                return render_to_response('assessment/editaff.html',{'getdetails':getdetails})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def getaffective2(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.expensedecription
        varerr =''
        getdetails = SubjectScore.objects.get(id = vid)
        if request.method == 'POST':
            ca1 = request.POST['firstca']
            ca2 = request.POST['secondca']
            exam = request.POST['exam']
            if exam == "":
                exam = 0
            if ca1 == "":
                ca1 = 0
            if ca2 == "":
                ca2 = 0
            try:
                h = int(exam)
            except :
                return HttpResponseRedirect('/reportsheet/enterca/')
            try:
                h1 = int(ca1)
            except :
                return HttpResponseRedirect('/reportsheet/enterca/')
            try:
                h2 = int(ca2)
            except :
                return HttpResponseRedirect('/reportsheet/enterca/')
            if h > 60 :
                h = 60
            if h1 > 20 :
                h1 = 20
            if h2 > 20 :
                h2 = 20
            getdetails.first_ca = h1
            getdetails.second_ca = h2
            getdetails.exam_score = h
            getdetails.save()
            return HttpResponseRedirect('/reportsheet/enterca/')
        else:
            form = caform()

        return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')


def getpsyco(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']


                dent = tblde.objects.get(id=1)
                if dent.status == 1:

                    getdetails = PsychomotorSkill.objects.get(id = acccode)
                    return render_to_response('assessment/editpsyco.html',{'getdetails':getdetails})

                else:
                    return render_to_response('assessment/noedit.html')

            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def getcomment(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                getdetails = StudentAcademicRecord.objects.get(id = acccode)
                student = getdetails.student.id


                dent = tblde.objects.get(id=1)
                if dent.status == 1:

                    if getdetails.term == 'First':
                        term=   'Second'
                        pt='First'

                    elif getdetails.term=='Second':
                        term = 'Third'
                        pt='Second'

                    elif getdetails.term=='Third':
                        term = 'First'
                        pt='Third'

                    # getdetails = StudentAcademicRecord.objects.get(student = student, term = term) #next term
                    getdetails2 = StudentAcademicRecord.objects.get(student = student, term = pt) #current term
                    getdetails = tblterm.objects.get(term =term)
                    return render_to_response('assessment/editcomment.html',{
                        'current_term':getdetails2,
                        'next_term':getdetails})
                else:
                    return render_to_response('assessment/noedit.html')
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def getcommentca(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                vid,ca =acccode.split(':')
                getdetails = StudentAcademicRecord.objects.get(id = vid)
                dit=getdetails.stu_ave1 * 5

                dent = tblde.objects.get(id=1)
                if dent.status == 1:
                    if ca == 'Mid term':
                        return render_to_response('assessment/edicacom.html',{'ca':ca,'getdetails':getdetails,'dit':dit})
                    elif ca=='End term':
                        return render_to_response('assessment/editcacom.html',{'ca':ca,'getdetails':getdetails})

                else :
                    return render_to_response('assessment/noedit.html')

            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')


def editcomment_old(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        varerr =''
        getdetails = ''
        if request.method == 'POST':
            comments = request.POST['class_teacher_comment']
            noopen = request.POST['noopen']
            nopresent = request.POST['nopresent']
            nexttem = request.POST['nexttem']
            tday = ''
            if nexttem == "":
                tday = datetime.date.today()
            else:
                rday,rmonth,ryear = nexttem.split('-')
                tday = int(ryear),int(rmonth),int(rday)
            if comments == "" or nopresent == "" or noopen == "" :
                return HttpResponseRedirect('/reportsheet/comment/')
            try:
                j = int(noopen)
            except :
                j = 0
            try:
                k = int(nopresent)
            except :
                k = 0
            l = j - k
            getdetails = StudentAcademicRecord.objects.get(id = vid)
            session = getdetails.session
            term = getdetails.term
            getdetails.class_teacher_comment = comments
            getdetails.days_open = j
            getdetails.days_present = k
            getdetails.days_absent = l
            getdetails.next_term_start=tday
            getdetails.save()
            StudentAcademicRecord.objects.filter(session = session,term = term).update(next_term_start = tday)

            return HttpResponseRedirect('/reportsheet/ca_comments/')
        else:
            form = caform()
        return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')


def editcomment(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        varerr =''
        getdetails = ''
        if request.method == 'POST':
            comments = request.POST['class_teacher_comment']
            absent = request.POST['noabsent']
            if comments == "" or absent == "":
                return HttpResponseRedirect('/reportsheet/ca_comments/')

            getdetails = StudentAcademicRecord.objects.get(id = vid)
            session = getdetails.session
            term = getdetails.term

            getdetails.days_present = int(getdetails.days_open) - int(absent)
            getdetails.class_teacher_comment = comments
            getdetails.days_absent = absent
            getdetails.save()
            # StudentAcademicRecord.objects.filter(session = session,term = term).update(next_term_start = tday)

            return HttpResponseRedirect('/reportsheet/ca_comments/')
        else:
            form = caform()
        return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')

def editcommentca1(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        varerr =''
        getdetails = ''
        if request.method == 'POST':
            comments = request.POST['comment']
            getdetails = StudentAcademicRecord.objects.filter(id = vid).update(com1=comments)
            return HttpResponseRedirect('/reportsheet/ca_comments/')
    else:
        return HttpResponseRedirect('/login/')

def editcommentca2(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        varerr =''
        getdetails = ''
        if request.method == 'POST':
            comments = request.POST['comment']
            getdetails = StudentAcademicRecord.objects.filter(id = vid).update(com2=comments)
            return HttpResponseRedirect('/reportsheet/ca_comments/')
    else:
        return HttpResponseRedirect('/login/')


def editpsyco(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        varerr =''
        getdetails = ''
        if request.method == 'POST':
            attendance = request.POST['attendance']
            motivation = request.POST['motivation']
            contribution = request.POST['contribution']
            social_behaviour = request.POST['social_behaviour']
            if contribution == "" or motivation == "" or attendance == "" or social_behaviour == "" :
                return HttpResponseRedirect('/reportsheet/affective/')
            getdetails = PsychomotorSkill.objects.get(id = vid)
            getdetails.attendance = attendance.upper()
            getdetails.motivation = motivation.upper()
            getdetails.contribution = contribution.upper()
            getdetails.social_behaviour = social_behaviour.upper()
            getdetails.save()
            return HttpResponseRedirect('/reportsheet/affective/')
        else:
            form = caform()

        return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')

def editaffective(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        varerr =''
        getdetails = ''
        if request.method == 'POST':
            punctuality = request.POST['punctuality']
            neatness = request.POST['neatness']
            honesty = request.POST['honesty']
            initiative = request.POST['initiative']
            self_control = request.POST['self_control']
            reliability = request.POST['reliability']
            perseverance = request.POST['perseverance']
            politeness = request.POST['politeness']
            attentiveness = request.POST['attentiveness']
            rel_with_people = request.POST['rel_with_people']
            cooperation = request.POST['cooperation']
            organizational_ability = request.POST['organizational_ability']
            if punctuality == "" or self_control == "" or initiative == "" or honesty == "" or neatness == "" or reliability == "" or perseverance == "" or politeness == "" or attentiveness == "" or rel_with_people == ""  or cooperation =="" or organizational_ability =="":
                return HttpResponseRedirect('/reportsheet/affective/')
            getdetails = AffectiveSkill.objects.get(id = vid)
            getdetails.punctuality = punctuality.upper()
            getdetails.neatness = neatness.upper()
            getdetails.honesty = honesty.upper()
            getdetails.initiative = initiative.upper()
            getdetails.self_control = self_control.upper()
            getdetails.reliability = reliability.upper()
            getdetails.perseverance = perseverance.upper()
            getdetails.politeness = politeness.upper()
            getdetails.attentiveness = attentiveness.upper()
            getdetails.rel_with_people = rel_with_people.upper()
            getdetails.cooperation = cooperation.upper()
            getdetails.organizational_ability = organizational_ability.upper()
            getdetails.save()
            return HttpResponseRedirect('/reportsheet/affective/')
        else:
            form = caform()
        return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')

def addsubject(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        try:
            if Student.objects.get(fullname=varuser,admitted_session=currse,gone=False):
                return HttpResponseRedirect('/reportsheet/student/my_subjects/')
        except:
            if ClassTeacher.objects.filter(teachername = varuser).count() == 0 :
                return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails =''
        form = addsubjectform()
        return render_to_response('assessment/addsubject.html',{'varuser':varuser,'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')

def addstudentsubject(request):
    if  "userid" in request.session:
        varuser = request.session['userid']

        user = userprofile.objects.get(username = varuser)
        uenter = user.expensedecription


        if ClassTeacher.objects.filter(teachername = varuser).count() == 0 :
            return HttpResponseRedirect('/reportsheet/access-denied/')

        varerr =''
        getdetails =''
        if request.method == 'POST':
            form = addsubjectform(request.POST) # A form bound to the POST data
            if form.is_valid():
                expenses = form.cleaned_data['expenses']
                return HttpResponseRedirect('/bill/expensesname/')
        else:
            form = addsubjectform()
        return render_to_response('assessment/addsubject.html',{'varuser':varuser,'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')

def getstudentsubject(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                post = request.POST.copy()
                acccode = post['userid']
                session,klass,arm,term = acccode.split(':')
                kk = []

                if term =='First':
                    data = Student.objects.filter(admitted_session = session,admitted_class = klass,first_term=True,admitted_arm = arm,gone = False).order_by('fullname')
                elif term == 'Second':
                    data = Student.objects.filter(admitted_session = session,admitted_class = klass,second_term=True,admitted_arm = arm,gone = False).order_by('fullname')

                elif term=='Third':
                    data = Student.objects.filter(admitted_session = session,admitted_class = klass,third_term=True,admitted_arm = arm,gone = False).order_by('fullname')

                for p in data:
                    kk.append(p.fullname)
                return HttpResponse(json.dumps(kk), mimetype='application/json')
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')


def getsubject4student(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                getdetails = ''
                post = request.POST.copy()
                acccode = post['userid']
                session,klass,arm,term,student = acccode.split(':')
                getstu = Student.objects.get(admitted_class = klass,admitted_arm=arm,admitted_session = session,fullname = student,gone = False)
                if StudentAcademicRecord.objects.filter(student = getstu,term = term):
                   comm = StudentAcademicRecord.objects.get(student = getstu,term = term)
                   getdetails = SubjectScore.objects.filter(session = session,klass = klass, arm = arm,term = term,academic_rec = comm).order_by('num')
                return render_to_response('assessment/subject.html',{'varuser':varuser,'getdetails':getdetails,'stuid':getstu.id,'fullname':getstu.fullname,'session':session,'term':term})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')


def editsubgrp(request,invid):
    varerr =""
    if  "userid" in request.session:
        varuser = request.session['userid']
        varerr =""
        if request.method == 'POST':
            cate = request.POST['subjectlist']
            getdetails = SubjectScore.objects.get(id = invid)
            getdetails.subject_group=cate
            getdetails.save()
            return HttpResponseRedirect('/reportsheet/class_list/')
        else:
            return HttpResponseRedirect('/setup/subject/')
    else:
        return HttpResponseRedirect('/login/')


def changesubgrp(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                getdetails =  SubjectScore.objects.get(id = acccode)
                subjectlist = Subject_group.objects.all().order_by('id')
                fs = {}
                for k in subjectlist:
                    l = {k.subject_group:k.subject_group}
                    fs.update(l)
                nlist = fs.keys()
                return render_to_response('assessment/changegrp.html',{'varuser':varuser,'subjectlist':nlist,'varerr':varerr,'getdetails':getdetails})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')


def getmorestudentsubject(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                code = post['userid']
                acccode,ter = str(code).split(':')
                getstu = Student.objects.get(id = acccode)
                session = getstu.admitted_session
                admno = getstu.admissionno
                klass = getstu.admitted_class
                subclass = getstu.subclass
                arm = getstu.admitted_arm
                term = ter
                fullname = getstu.fullname
                subjectlist = Subject.objects.filter(category = subclass, category2 = 'Optional').order_by('num')
                fs = {}
                for k in subjectlist:
                    l = {k.subject:k.subject}
                    fs.update(l)
                nlist = fs.keys()
                chk=tblcf.objects.get(session=session,term=term)
                chkdate = chk.deadline
                if chkdate < date:
                    return render_to_response('assessment/checkbackcf.html',{'ckk':chkdate})

                return render_to_response('assessment/moresubject.html',{'session':session,
                    'fullname':fullname,
                    'admno':admno,
                    'subjectlist':nlist,
                    'klass':klass,
                    'subclass':subclass,
                    'arm':arm,
                    'term':ter})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')




def getmoresubject(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                code = post['userid']
                acccode,ter = str(code).split(':')
                getstu = Student.objects.get(id = acccode)
                session = getstu.admitted_session
                admno = getstu.admissionno
                klass = getstu.admitted_class
                subclass = getstu.subclass
                arm = getstu.admitted_arm
                term = ter
                fullname = getstu.fullname

                dent = tblde.objects.get(id=1)
                if dent.status == 1:


                    subjectlist = Subject.objects.filter(category = subclass, category2 = 'Optional').order_by('num')
                    fs = {}
                    for k in subjectlist:
                        l = {k.subject:k.subject}
                        fs.update(l)
                    nlist = fs.keys()
                    return render_to_response('assessment/moresubject.html',{'session':session,'fullname':fullname,'admno':admno,'subjectlist':nlist,'klass':klass,'subclass':subclass,'arm':arm,'term':term})
                else:
                    return render_to_response('assessment/noedit.html')


            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')






def addmoresubject(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        # user = userprofile.objects.get(username = varuser)
        # uenter = user.expensedecription
        varerr =''
        getdetails =''
        term_l = ['First','Second','Third']
        term_2 = ['Second','Third']
        if request.method == 'POST':
            admno = request.POST['admno']
            session = request.POST['session']
            term1 = request.POST['term']
            subclass = request.POST['subclass']
            subjectlist = request.POST['subjectlist']


            stuacarec = Student.objects.get(admissionno = admno,
                admitted_session = session,
                gone=False)
            # if term == 'First':

            for tt in term_l:
                try:
                    StudentAcademicRecord.objects.get(student = stuacarec,term = tt)

                except:
                    StudentAcademicRecord(student=stuacarec,
                        klass=stuacarec.admitted_class,
                        arm=stuacarec.admitted_arm,
                        term=tt,
                        session=stuacarec.admitted_session).save()


                    academic_record=StudentAcademicRecord.objects.get(student=stuacarec,term=tt)

                    AffectiveSkill(academic_rec=academic_record).save()
                    PsychomotorSkill(academic_rec=academic_record).save()

            gets = Subject.objects.get(subject = subjectlist,category=subclass)

            num = gets.num

            if term1 == 'First':
                for tk in term_l:
                    stuac = StudentAcademicRecord.objects.get(student = stuacarec,term = tk)

                    try:

                        SubjectScore.objects.get(academic_rec = stuac,
                            term = tk,
                            subject = subjectlist)

                    except:

                           SubjectScore(academic_rec = stuac,
                            term = tk,
                            subject = subjectlist,
                            num = num,
                            session = session,
                            klass = stuacarec.admitted_class,
                            arm = stuacarec.admitted_arm).save()


            elif term1 == 'Second':
                for tk in term_2:
                    stuac = StudentAcademicRecord.objects.get(student = stuacarec,term = tk)

                    try:

                        SubjectScore.objects.get(academic_rec = stuac,
                            term = tk,
                            subject = subjectlist)

                    except:

                           SubjectScore(academic_rec = stuac,
                            term = tk,
                            subject = subjectlist,
                            num = num,
                            session = session,
                            klass = stuacarec.admitted_class,
                            arm = stuacarec.admitted_arm).save()


            elif term1 == 'Third':

                stuac = StudentAcademicRecord.objects.get(student = stuacarec,term = term1)

                try:

                    SubjectScore.objects.get(academic_rec = stuac,
                        term = term1,
                        subject = subjectlist)

                except:

                       SubjectScore(academic_rec = stuac,term = term1,
                        subject = subjectlist,num = num,
                        session = session,
                        klass = stuacarec.admitted_class,
                        arm = stuacarec.admitted_arm).save()


            return HttpResponseRedirect('/reportsheet/secondary_cf/%s/%s/%s/'%(str(session).replace('/','j'),str(admno).replace('/','k'),str(term1).replace(' ','m')))
        else:
            form = addsubjectform()
        return render_to_response('assessment/addsubject.html',{'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')








def secondary_cf(request,session,admn,term):
    varuser = request.session['userid']
    sec = ''
    for j in appused.objects.all():
        sec = j.secondary
    if sec is True :
        pass
    else:
        return HttpResponseRedirect('/reportsheet/access-denied/')
    session = str(session).replace('j','/')
    admno = str(admn).replace('k','/')
    term = str(term).replace('m',' ')
    stud = Student.objects.get(admissionno=admno,admitted_session=session,gone=False)
    acadec = StudentAcademicRecord.objects.get(student=stud,term=term)
    cf = SubjectScore.objects.filter(academic_rec=acadec,term =term)
    return render_to_response('assessment/stu_sub.html',{'getdetails':cf,'stuid':stud.id,'session':stud.admitted_session,'arm':stud.admitted_arm, 'varuser':varuser,'admno':admno,'term':term,'name':stud.fullname,'klass':stud.admitted_class})




def deletemoresubject(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                getstu = SubjectScore.objects.get(id = acccode)
                session = getstu.academic_rec.student.admitted_session
                admno = getstu.academic_rec.student.admissionno
                klass = getstu.academic_rec.student.admitted_class
                subject = getstu.subject
                arm = getstu.academic_rec.student.admitted_arm
                term = getstu.term
                fullname = getstu.academic_rec.student.fullname

                dent = tblde.objects.get(id=1)
                if dent.status == 1:
                    return render_to_response('assessment/deletemoresubject.html',{'session':session,'fullname':fullname,'admno':admno,'klass':klass,'arm':arm,'term':term,'subject':subject,'id':acccode})
                else:
                    return render_to_response('assessment/noedit.html')
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def confirmdeletemoresubject(request,pid):
    if  "userid" in request.session:
        getstu = SubjectScore.objects.get(id = pid)
        session = getstu.academic_rec.student.admitted_session
        admno = getstu.academic_rec.student.admissionno
        term1=getstu.term
        getstu.delete()
        return HttpResponseRedirect('/reportsheet/secondary_cf/%s/%s/%s/'%(str(session).replace('/','j'),str(admno).replace('/','k'),str(term1).replace(' ','m')))
    else:
        return HttpResponseRedirect('/login/')

def principalcomment(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.expensedecription
        if Principal.objects.filter(teachername = varuser).count() == 0:
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails =''
        if request.method == 'POST':
            form = caform(request.POST) # A form bound to the POST data
            if form.is_valid():
                expenses = form.cleaned_data['expenses']
                return HttpResponseRedirect('/bill/expensesname/')
        else:
            form = caform()
        return render_to_response('assessment/principalcomment.html',{'varuser':varuser,'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')

def getstudentprincipalcomment(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                session,klass,arm,term = acccode.split(':')
                #print klass
                data = []
                getstu = Student.objects.filter(admitted_class = klass,admitted_arm=arm,admitted_session = session,gone = False).order_by('-sex','fullname')
                for p in getstu:
                    if StudentAcademicRecord.objects.filter(student = p,term = term):
                        comm = StudentAcademicRecord.objects.get(student = p,term = term)
                        stdic = {'studentinfo':p,'comment':comm}
                        data.append(stdic)
                return render_to_response('assessment/princomment.html',{'data':data})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def getprincipalcomment(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                getdetails = StudentAcademicRecord.objects.get(id = acccode)
                # print getdetails
                return render_to_response('assessment/editprincipalcomment.html',{'getdetails':getdetails})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:

            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def editcommentprin(request,vid):
    if  "userid" in request.session:
        varuser = request.session['userid']
        varerr =''
        getdetails = ''
        if request.method == 'POST':
            comments = request.POST['class_teacher_comment']
            if comments == "":
                return HttpResponseRedirect('/reportsheet/affective/')
            getdetails = StudentAcademicRecord.objects.get(id = vid)
            getdetails.principal_comment = comments
            getdetails.save()
            return HttpResponseRedirect('/reportsheet/principalcomment/')
        else:
            form = caform()

        return render_to_response('assessment/editca.html',{'form':form,'varerr':varerr,'getdetails':getdetails})
    else:
        return HttpResponseRedirect('/login/')

def getstudentacademic(request):#*******************now
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                getdetails = StudentAcademicRecord.objects.get(id = acccode)
                academic = SubjectScore.objects.filter(academic_rec = getdetails).order_by('num')
                return render_to_response('assessment/academicrecord.html',{'getdetails':getdetails,'academic':academic})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def addsubject4pry(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.expensedecription
        if ClassTeacher.objects.filter(teachername = varuser).count() == 0 :
            return HttpResponseRedirect('/reportsheet/access-denied/')
        sec = ''
        pry = ''
        for j in appused.objects.all():
            pry = j.primary
            sec = j.secondary
        if pry is True :
            pass
        else:
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails =''
        if request.method == 'POST':
            form = addsubjectform(request.POST) # A form bound to the POST data
            if form.is_valid():
                expenses = form.cleaned_data['expenses']
                return HttpResponseRedirect('/bill/expensesname/')
        else:
            form = addsubjectform()
        return render_to_response('assessment/capry.html',{'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')

def getsubject4studentpry(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                getdetails = ''
                post = request.POST.copy()
                acccode = post['userid']
                session,klass,arm,term,student = acccode.split(':')
                getstu = Student.objects.get(admitted_class = klass,admitted_arm=arm,admitted_session = session,fullname = student)
                if StudentAcademicRecord.objects.filter(student = getstu,term = term):
                    comm = StudentAcademicRecord.objects.get(student = getstu,term = term)
                    getdetails = SubjectScore.objects.filter(session = session,klass = klass, arm = arm,term = term,academic_rec = comm).order_by('num')
                return render_to_response('assessment/subjectpry.html',{'getdetails':getdetails})
            else:
                gdata = ""
                return render_to_response('index.html',{'gdata':gdata})
        else:
            gdata = ""
            return render_to_response('getlg.htm',{'gdata':gdata})
    else:
        return HttpResponseRedirect('/login/')

def getclassaffpry(request):
    if  "userid" in request.session:
        if request.is_ajax():
            if request.method == 'POST':
                varuser = request.session['userid']
                varerr =""
                post = request.POST.copy()
                acccode = post['userid']
                state = acccode
                kk = []
                sdic = {}
                data = ClassTeacher.objects.filter(teachername = varuser,session = state).exclude(klass__startswith ='J').exclude(klass__startswith ='S').order_by('klass')
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


def indreport(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user= userprofile.objects.get(username=varuser)
        uenter = user.reportsheet
        if uenter is False:
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr = ''
        getdetails= ''
        bal = 250

        school = get_object_or_404(School,pk=1)
        if request.method == 'POST':
            form = indreportform(request.POST)
            if form.is_valid():
                session = form.cleaned_data['session']
                term = form.cleaned_data['term']
                admno = form.cleaned_data['admno']
                Pin = form.cleaned_data['Pin']
                replist = []
                varclas=[]
                varused= 0
                varurem = 0
                if Student.objects.filter(admissionno=admno,admitted_session=session).count()==0:
                    varerr= 'ADMISSION NUMBER NOT FOUND'
                    form = indreportform()
                    return render_to_response ('assessment/indreport.html',{'form':form, 'varerr':varerr})


                if tblrpin.objects.filter(rpin=Pin).count()== 0:
                    varerr= 'PLEASE CHECK THE PIN AND TRY AGAIN'
                    return render_to_response('assessment/indreport.html',{'varerr':varerr,'form':form})


                if tblexpress.objects.filter(pin = Pin):
                    usd = tblexpress.objects.get(pin=Pin)
                    usdpin = usd.pin
                    usdterm = usd.term
                    usdsession = usd.session
                    usdadmno = usd.admno
                    if usdadmno == admno and usdterm==term and usdsession==session and usdpin==Pin:
                        varu = count( Pin)
                        if varu >='5':
                           varerr= 'PIN ALREADY USED '+ varu + ' TIMES'
                           return render_to_response('assessment/indreport.html',{'varerr':varerr,'form':form})
                        else:
                            varused= int(varu) +1
                            tblexpress.objects.filter(pin=  Pin).update(count= varused)
                            varurem =5 - varused
                    else:
                       varerr= 'THIS PIN HAS BEEN USED'
                       return render_to_response('assessment/indreport.html',{'varerr':varerr,'form':form})
                else:
                    totbil = printbill (admno,session,term)
                    allowable_debt = 0.15 * int(totbil)
                    allowable_debt = locale.format('%.0f',allowable_debt)
                    allowable_debt= int(allowable_debt) # what i can owe

                    acc=tblaccount.objects.get(acccode = admno)
                    actual_debt = acc.accbal
                    actual_debt = int(actual_debt) # what i'm actually owing
                    bal = actual_debt
                    if allowable_debt <= actual_debt:
                        varerr = "KINDLY UPDATE YOUR WARD'S ACCOUNT " #+totbil+ '  ' +str(actual_debt)
                        return render_to_response('assessment/indreport.html',{'varerr':varerr,'form':form})
                    else:
                        st = Student.objects.get(admissionno=admno, admitted_session=session)
                        tblexpress(count=1,session=session, admno=admno, klass=st.admitted_class, term=term,pin=Pin).save()
                        varurem = 4

              ##########  calc. total bill for the term ******************
                totbil = printbill (admno,session,term)
                allowable_debt = 0.15 * int(totbil)
                allowable_debt = locale.format('%.0f',allowable_debt)
                allowable_debt= int(allowable_debt) # what i can owe
############## cal account balaance *************************************
                acc=tblaccount.objects.get(acccode = admno)
                actual_debt = acc.accbal
                actual_debt = int(actual_debt) # what i'm actually owing
                bal = actual_debt


                classtot = 0
                totsub = 0
                totalmarkcount = 0
                st = Student.objects.get(admissionno=admno, admitted_session=session)
                if term == "First":
                    stuno1 = Student.objects.filter(
                        admitted_session = session,
                        first_term = 1, admitted_class = st.admitted_class,
                        admitted_arm = st.admitted_arm,gone = False).count()
                    stuinfo = Student.objects.get(
                        admitted_session = session,
                        admissionno = admno,
                        first_term = 1)
                elif term == "Second":
                    stuno1 = Student.objects.filter(admitted_session = session,second_term = 1, admitted_class = st.admitted_class,admitted_arm = st.admitted_arm,gone = False).count()
                    stuinfo = Student.objects.get(admitted_session = session, admissionno = admno, second_term = 1)
                else:
                    stuno1 = Student.objects.filter(admitted_session = session,third_term = 1,term = term, admitted_class = varclass,admitted_arm = vararm,gone = False).count()
                    stuinfo = Student.objects.get(admitted_session = session, admissionno = admno, third_term = 1,term=term)
                varclass= stuinfo.admitted_class
                vararm = stuinfo.admitted_arm
                varclas=varclass[0]
                getgrading=gradingsys.objects.filter(classsub__startswith = varclas)

                if StudentAcademicRecord.objects.filter(student = stuinfo,term = term):
                    acaderec = StudentAcademicRecord.objects.get(student = stuinfo,term = term)
                    affskill = AffectiveSkill.objects.get(academic_rec = acaderec)
                    psycho = PsychomotorSkill.objects.get(academic_rec = acaderec)
                    subsco = SubjectScore.objects.filter(academic_rec = acaderec,term = term).order_by('num')
                    totsub = SubjectScore.objects.filter(academic_rec = acaderec,term = term).count()
                    totalmark2 = 0
                    if SubjectScore.objects.filter(academic_rec = acaderec,session = session,term = term):
                        totalmark = SubjectScore.objects.filter(academic_rec = acaderec,session = session,term = term).aggregate(Sum('end_term_score'))
                        totalmark2 = totalmark['end_term_score__sum']
                        totalmarkcount = SubjectScore.objects.filter(academic_rec = acaderec,session = session,term = term).count()
                        rtotal = int(totalmark2)
                        if float(totsub) == 0:
                            perc = 0
                        else:
                            perc = float(rtotal)/float(totsub)
                        classtot += rtotal
                        ks = totalmarkcount * 100
                        totsub += ks
                        jdic = {'studentinfo':stuinfo,'academic':acaderec,'affective':affskill,'pyscho':psycho,'subject':subsco,'totalmark':rtotal,'getgrading':getgrading,'percentage':locale.format("%.2f",perc,grouping=True)}
                        replist.append(jdic)
                if classtot == 0 or stuno1 == 0:
                   clavg = 0.0
                else:
                    j = classtot/stuno1
                    clavg =j/float(totalmarkcount)


                #varclas= varclass[0]

                if varclas == 'S':
                    return render_to_response('assessment/reportsss.html',{'form':form,'varu':varurem,'varerr':varerr,'replist':replist,'school':school,'term':term,'stuno':stuno})

                if varclas == 'N' or varclas == 'K' or varclas == 'P':
                    return render_to_response('assessment/reportnpin.html',{'form':form,'varclas':varclas,'varu':varurem,'bal':bal,'pin':Pin,'varerr':varerr,'replist':replist,'school':school,'term':term,'stuno1':stuno1,'classavg':locale.format("%.2f",clavg,grouping=True)})

                if varclas =='J':
                    return render_to_response('assessment/reportpin.html',{'form':form,'varclas':varclas,'varu':varurem,'bal':bal,'pin':Pin,'varerr':varerr,'replist':replist,'school':school,'term':term,'stuno1':stuno1,'classavg':locale.format("%.2f",clavg,grouping=True)})


            else:
                varerr='FILL OUT ALL BOXES'
                return render_to_response('assessment/indreport.html',{'form':form, 'varerr':varerr})
        else:
            form = indreportform()
            return render_to_response('assessment/indreport.html',{'form':form,})
    else:
        return HttpResponseRedirect('/login/')

def reportopt(request):
    if "userid" in request.session:
        return render_to_response('assessment/select.html')
    else:
        return HttpResponseRedirect('/login/')

        # user=userprofile.objects.get(username=varuser)
        # uenter=user.createuser
        # if uenter is False:
        #     return HttpResponseRedirect('/welcome/')



def reportsheet(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.createuser

        klassteacher = ClassTeacher.objects.filter(teachername=varuser).count()



        if uenter is False :
            if klassteacher == 0:
                return HttpResponseRedirect('/reportsheet/access-denied/')

        varerr =''
        getdetails =''
        # school = get_object_or_404(School, pk=1)
        school=School.objects.get(id =1)
        if request.method == 'POST':
            form = reportsheetform(request.POST)
            if form.is_valid():
                session = form.cleaned_data['session']
                klass = form.cleaned_data['klass']
                term = form.cleaned_data['term']
                arm = form.cleaned_data['arm']
                try:
                  codi = ClassTeacher.objects.get(klass=klass,session=session,teachername='N/A')
                except:
                  codi= 'Not Set'
                replist = []

                varbeg = klass[0]

                getgrading = gradingsys.objects.filter(classsub__startswith = varbeg)

                # processall(session,term,klass,arm,reporttype)

                gh = tblrunp.objects.filter(session = session,
                    klass=klass,
                    term=term,
                    arm=arm, reportsheet='End term')

                gh_count =gh.count()

                dddt = datetime.datetime.now()
                mytime = dddt.time()


                if gh_count == 1:
                    gh_new = gh.get(session=session,
                        klass=klass,
                        arm=arm,
                        term=term,
                        reportsheet='End term')

                    if gh_new.status == 1:
                        endtermstats(session,term,klass,arm)


                    gh_new.status=0
                    # gh_new.time=mytime
                    gh_new.save()

                else:

                    tblrunp(session = session,
                        klass=klass,
                        term=term,
                        arm=arm,
                        time=mytime,
                        status = 0,
                        reportsheet='End term').save()

                    endtermstats(session,term,klass,arm)



                if term == 'First':

                    stuinfo = Student.objects.filter(first_term = True,
                        admitted_session = session,
                        admitted_class = klass,
                        admitted_arm = arm,
                        gone = False).order_by('fullname')


                    for j in stuinfo:
                        acaderec = StudentAcademicRecord.objects.get(session=session,student = j,term = 'First')
                        affective=AffectiveSkill.objects.get(academic_rec=acaderec)
                        sycho= PsychomotorSkill.objects.get(academic_rec=acaderec)

                        if session =='2023/2024' and varbeg == 'J':
                            subsco = SubjectScore.objects.filter(academic_rec = acaderec).exclude(subject='MUSIC').order_by('num')
                        else:
                            subsco = SubjectScore.objects.filter(academic_rec = acaderec).order_by('num')

                        totalmark12 = 0
                        if SubjectScore.objects.filter(academic_rec=acaderec, term='First').count()>0:
                            totalmark = SubjectScore.objects.filter(academic_rec = acaderec, term='First').aggregate(Sum('end_term_score'))
                            totalmark12 = totalmark['end_term_score__sum']
                            totalmark12 = int(totalmark12)


                        stave=acaderec.stu_ave2

                        if varbeg == 'S':
                            st_grade = studentaveragedrader(float(stave))  #grading student average
                        elif varbeg=='J':
                            st_grade = juniorgrade(float(stave))

                        stat={'st_grade':st_grade['grade']}
                        # stustat.append(stat)



                        jdic = {'totalmark':totalmark12,
                        'studentinfo':j,
                        'affective':affective,
                        'sycho':sycho,
                        'codi':codi,
                        'grading':getgrading,
                        'academic':acaderec,
                        'school':school,
                        'st_grade':stat,
                        'subject':subsco}

                        replist.append(jdic)

                    next_term = tblterm.objects.get(term = 'Second')
                    next_term=next_term.start_date


                    if varbeg=='J':
                        return render_to_response('assessment/mysummarysheet.html',{
                            'varuser':varuser,
                            'form':form,
                            'date':date,
                            'varerr':varerr,
                            'replist':replist,
                            'term':term.upper(),
                            'next_term':next_term})


                    elif varbeg=='S':
                        return render_to_response('assessment/reportpin.html',{
                            'varuser':varuser,
                            'form':form,
                            'date':date,
                            'varerr':varerr,
                            'replist':replist,
                            'term':term.upper(),
                            'next_term':next_term})

                elif term=='Second':
                    stuinfo = Student.objects.filter(second_term = True,
                        admitted_session = session,
                        admitted_class = klass,
                        admitted_arm = arm,
                        gone = False).order_by('fullname')

                    for j in stuinfo:
                        acaderec = StudentAcademicRecord.objects.get(student = j,
                            term = 'Second',
                            session=session)

                        if session =='2023/2024' :
                            if  varbeg == 'J':
                                subsco = SubjectScore.objects.filter(academic_rec = acaderec).exclude(subject='MUSIC').order_by('num')
                            elif varbeg == 'S':
                                subsco = SubjectScore.objects.filter(academic_rec = acaderec).exclude(subject='GEOGRAPHY').order_by('num')


                        sycho = PsychomotorSkill.objects.get(academic_rec=acaderec)

                        affective=AffectiveSkill.objects.get(academic_rec=acaderec)


                        stave=acaderec.stu_ave2


                        if varbeg == 'S':
                            st_grade = studentaveragedrader(float(stave))  #grading student average
                        elif varbeg=='J':
                            st_grade = juniorgrade(float(stave))


                        stat={'stu_grade':st_grade['grade']}


                        festrec='False'
                        try:
                            acaderec1 = StudentAcademicRecord.objects.get(student =j,
                                term = 'First', session=session)
                        except:
                            festrec='True'

                        totalmark2 = 0

                        # totalmark = SubjectScore.objects.filter(academic_rec = acaderec)
                        totalmark= subsco.aggregate(Sum('end_term_score'))
                        totalmark2 = totalmark['end_term_score__sum']
                        totalmark2 = int(totalmark2)

                        totalmark12 = 0


                        if festrec=='False': #IE FIRST TERM RECORD FOUND
                            try:
                                totalmarkk = SubjectScore.objects.filter(academic_rec = acaderec1,
                                    term='First',
                                    session=session).aggregate(Sum('end_term_score'))
                                totalmark12 = totalmarkk['end_term_score__sum']
                                totalmark12 = int(totalmark12)
                            except:
                                totalmark12 = 0

                        else:
                            totalmark12=0

                        secsublist = []
                        secdic = {}

                        for h in subsco:
                            if festrec=='True': #IE NO FIRST TERM RECORD
                                fscore = '-'
                            else:
                                try:
                                    fsc = SubjectScore.objects.get(academic_rec = acaderec1,term = 'First',subject = h.subject,session=session)
                                    fsco = fsc.end_term_score
                                    fscore = str(fsco)
                                except:
                                    fscore = '-'

                            secdic ={'secondterm':h,'firstterm':fscore}
                            secsublist.append(secdic)



                        jdic = {'totalmark2':totalmark2,
                        'totalmark1':totalmark12,
                        'studentinfo':j,
                        'school':school,
                        'affective':affective,
                        'sycho':sycho,
                        'codi':codi,
                        'stu_grade':stat,
                        'grading':getgrading,
                        'academic':acaderec,
                        'subject':secsublist}

                        replist.append(jdic)

                        next_term = tblterm.objects.get(term = 'Third')
                        next_term=next_term.start_date



                    if varbeg=='J':

                        return render_to_response('assessment/reportnsecond.html',{'varuser':varuser,
                            'next_term':next_term,
                            'form':form,
                            'stave':stave,
                            'date':date,
                            'varerr':varerr,
                            'replist':replist,
                            'term':term})

                    elif varbeg=='S':
                        return render_to_response('assessment/reportnviewsecond.html',{'varuser':varuser,
                            'form':form,
                            'date':date,
                            'next_term':next_term,
                            'varerr':varerr,
                            'replist':replist,
                            'term':term})



                elif term =='Third':
                    ssu =0
                    ssa=0
                    ssp=0

                    ## Times school opened**********
                    fg = tblterm.objects.filter(session=session)
                    for g in fg:
                        ssu = ssu+ int(g.duration)

                    stuinfo = Student.objects.filter(third_term = True,
                    admitted_session = session,
                    admitted_class = klass,
                    admitted_arm = arm,gone = False)#.order_by('fullname')


                    next_term = tblterm.objects.get(term = 'First')
                    ntb=next_term.start_date

                    class_scores = 0
                    allkt = 0
                    sum_of_subject_averages=0
                    sum_of_subject_averages_class=0

                    subject_total=0

                    for j in stuinfo:
                        acadep = StudentAcademicRecord.objects.filter(student = j,session=session)

                        if acadep.count() == 0:
                            ssa = 0
                            ssp=0
                        else:
                            ssa = acadep.aggregate(Sum('days_absent'))
                            ssa = ssa['days_absent__sum']

                            ssp = acadep.aggregate(Sum('days_present'))
                            ssp = ssp['days_present__sum']



                        acaderec = acadep.get(term = term)
                        affskill = AffectiveSkill.objects.get(academic_rec = acaderec)
                        psycho = PsychomotorSkill.objects.get(academic_rec = acaderec)
                        subsco = SubjectScore.objects.filter(academic_rec = acaderec,term = term,session = session).order_by('num')




                        firstrec='False'  ##OBTAINING FIRST TERM RECORDS *******************
                        secrec='False'
                        try:
                            acaderec1 = StudentAcademicRecord.objects.get(student = j,term = 'First',session=session)
                        except:
                            firstrec='True'


                        try:
                            acaderec2 = StudentAcademicRecord.objects.get(student = j,term = 'Second',session=session)
                        except:
                            secrec='True'

                        secsublist = []
                        secdic = {}

                        for h in subsco:
                            if firstrec=='True':
                                fscore = '-'
                            else:
                                try:

                                    fsc = SubjectScore.objects.get(session=session, academic_rec = acaderec1,term = 'First',subject = h.subject)
                                    fsco = fsc.end_term_score
                                    fscore = str(fsco)
                                except:
                                    fscore='-'

                            if secrec=='True':
                                fscoret = '-'
                            else:
                                try:
                                    fsct = SubjectScore.objects.get(session=session, academic_rec = acaderec2,term = 'Second',subject = h.subject)
                                    fscot = fsct.end_term_score
                                    fscoret = str(fscot)
                                except:
                                    fscoret = '-'
                            secdic ={'thirdterm':h,'firstterm':fscore,'secondterm':fscoret}
                            secsublist.append(secdic)





                        rtotals=0
                        totalmark = SubjectScore.objects.filter(academic_rec = acaderec,session = session,term = term).aggregate(Sum('end_term_score'))
                        totalmark2 = totalmark['end_term_score__sum']
                        rtotals = int(totalmark2)



                        #******total for first term*********************

                        totalmark2sec = 0
                        rtotalsec = 0


                        if firstrec=='False':# IE IF FIRST TERM RECORD IS FOUND
                            totalmarksec = SubjectScore.objects.filter(academic_rec = acaderec1,session = session,term = 'First').aggregate(Sum('end_term_score'))
                            totalmark2sec = totalmarksec['end_term_score__sum']
                            try:
                                rtotalsec = int(totalmark2sec)
                            except:
                                rtotalsec = 0
                        else:
                            rtotalsec = 0


                        #*******total for second term***************************
                        totalmark2sec1 = 0
                        rtotalsec1 = 0

                        if secrec=='False':#IE SECOND TERM RECORD IS FOUND
                            totalmarksec1 = SubjectScore.objects.filter(academic_rec = acaderec2,session = session,term = 'Second')
                            if totalmarksec1.count()>0:
                                totalmarksec1=totalmarksec1.aggregate(Sum('end_term_score'))
                                totalmark2sec1 = totalmarksec1['end_term_score__sum']
                                rtotalsec1 = int(totalmark2sec1)
                            else:
                                rtotalsec1 =0

                        else:
                            rtotalsec1 = 0

                        #*************************#annual average********************
                        totalmark24 = 0
                        rtotal4 = 0
                        totalmark4 = SubjectScore.objects.filter(academic_rec = acaderec,session = session,term = term).aggregate(Sum('end_term_score'))
                        totalmark24 = totalmark4['end_term_score__sum']
                        rtotal4 = float(totalmark24)



                        stave=subsco.count()
                        stave=rtotal4 / stave


                        if varbeg == 'S':
                            st_grade = studentaveragedrader(float(stave))  #grading student average
                        elif varbeg=='J':
                            st_grade = juniorgrade(float(stave))


                        stat={'st_grade':st_grade['grade']}


                        # t2t=Annual_statistics(session,j.admitted_class,j.admitted_arm,j.admissionno)

                        t2t=Annual_statistics(session,j.admitted_class,j.admissionno)

                        perf=[]


                        kt= 0
                        tottal_scores = 0

                        allfirst=0
                        allsecond=0
                        allthird =0


                        for subject in t2t:

                            acaderec = acadep.filter(term = 'First')
                            if acaderec.count()==1:
                                acaderec=acaderec.get()
                                p1= SubjectScore.objects.filter(session = session, academic_rec = acaderec,subject=subject,term='First')
                                if p1.count()==1:
                                    p1=p1.get()
                                    pf=p1.end_term_score
                                    if pf =='0':
                                        kt =kt +0
                                    else:
                                        kt =kt +1
                                    tottal_scores= tottal_scores+ int(pf)
                                    allfirst= allfirst + int(pf)
                                else:
                                    pf='N/A'
                            else:
                                pf ='N/A'


                            acaderec = acadep.filter(term = 'Second')
                            if acaderec.count() ==1:
                                acaderec=acaderec.get()
                                p2= SubjectScore.objects.filter(session = session, academic_rec = acaderec,subject=subject,term='Second')
                                if p2.count()==1:
                                    p2=p2.get()
                                    ps=p2.end_term_score
                                    if ps == '0':
                                        kt =kt +0
                                    else:
                                        kt = kt + 1

                                    tottal_scores= tottal_scores+ int(ps)
                                    allsecond=allsecond + int(ps)
                                else:
                                    ps='N/A'
                            else:
                                ps='N/A'


                            acaderec = acadep.filter(term = 'Third')
                            if acaderec.count() ==1:
                                acaderec=acaderec.get()
                                p3= SubjectScore.objects.filter(session = session, academic_rec = acaderec,subject=subject,term='Third')
                                if p3.count()==1:
                                    p3=p3.get()
                                    pt=p3.end_term_score
                                    if pt == '0':
                                        kt =kt +0
                                    else:
                                        kt =kt +1
                                    tottal_scores= tottal_scores+ int(pt)
                                    allthird =allthird + int(pt)

                                else:
                                    pt='N/A'
                            else:
                                pt='N/A'





                            if kt==0:
                                ave=  0
                            elif kt > 0:
                                ave=  float(tottal_scores) / kt

                            xc=SubjectScore.objects.filter(session = session, academic_rec = acaderec,subject=subject).update(annual_avg=ave)


                            if varbeg == 'S':
                                st_grade = studentaveragedrader(float(ave))  #grading student average
                            elif varbeg=='J':
                                st_grade = juniorgrade(float(ave))



                            d= {'subject':subject,
                            'first':pf,
                            'second':ps,
                            'third':pt,
                            'annual':locale.format("%.1f",ave,grouping=True),
                            'annual_grade':st_grade['grade'],
                            'annual_grade_remark':st_grade['remark']}

                            perf.append(d)

                            sum_of_subject_averages=sum_of_subject_averages + ave

                            sum_of_subject_averages_class=sum_of_subject_averages_class + ave

                            class_scores = class_scores+ tottal_scores
                            allkt =allkt + kt
                            tottal_scores = 0
                            kt = 0

                        annual_class_avg = class_scores / allkt

                        an_sc = allfirst + allsecond + allthird


                        an_avg= sum_of_subject_averages / len(t2t)

                        vvv=locale.format("%.1f",an_avg,grouping=True)


                        try:
                            ttt = StudentAnnualRecord.objects.get(student=j,klass=j.admitted_class,arm=j.admitted_arm,session=session)
                            ttt.anualaverage=vvv
                            ttt.save()
                        except:
                            StudentAnnualRecord(student=j,klass=j.admitted_class,arm=j.admitted_arm,session=session,annualaverage=vvv).save()

                        subject_total = subject_total + len(t2t)




                        if varbeg == 'S':
                            an_grade = studentaveragedrader(float(an_avg))  #grading student average
                        elif varbeg=='J':
                            an_grade = juniorgrade(float(an_avg))




                        # category= varbeg = 'JS'#klass[0:2]
                        category = klass[0:2]
                        ggg=klass[-1]

                        coms=tblcom.objects.filter(category=category)
                        mid=[]

                        for cat in coms:
                            fb= cat.krang.split('-')[0]
                            fb=int(fb)
                            mid.append(fb)
                        mida=sorted(mid)
                        pos=0
                        pos=min(mida, key=lambda x:abs(x-float(an_avg)))
                        varerr='DONE WITH ZERO ERRORS'
                        coma=tblcom.objects.filter(krang__startswith=pos,category=category)
                        idvar=[]
                        for h in coma:
                            idvar.append(h.id)
                        idvar=idvar
                        uid=0
                        uid = random.choice(idvar)
                        esther=tblcom.objects.get(id=uid)


                        if ggg == '1':
                            nxt = category + " " + '2'
                        elif ggg == '2':
                            nxt = category + " " + '3'



                        if an_grade['grade']=='F':
                            comment = esther.comment + ' Advice to repeat'
                        else:
                            comment=esther.comment + ' Promoted to ' + nxt









                        tt={'total':perf,
                            'total_score':tottal_scores,
                           'days_open':ssu,
                            'days_absent':ssa,
                            'days_present':ssp,
                            'totalfirst':allfirst,
                            'totalsecond':allsecond,
                            'totalthird':allthird,
                            'cummulative_comment':comment,
                            'total_subject_avg':locale.format("%.2f",sum_of_subject_averages,grouping=True),
                            'an_avg':locale.format("%.1f",an_avg,grouping=True),
                            'an_grade':an_grade['grade']}





                        #**********************************************
                        jdic = {'studentinfo':j,
                        'academic':acaderec,
                        'affective':affskill,
                        'sycho':psycho,
                        'subject':secsublist,
                        'st_grade':stat,
                        'totalmark':rtotals,
                        'totalmark1':rtotalsec,
                        'totalmark2':rtotalsec1,
                        'annualavg':locale.format("%.2f",rtotal4,grouping=True),
                        'getgrading':getgrading}


                        k = {'summary':jdic,'cummulative':tt}
                        replist.append(k)





                        an_avg=0
                        sum_of_subject_averages= 0





                    overall_class_avg = sum_of_subject_averages_class / subject_total

                    if klass[0] == 'S':
                        # if form.cleaned_data['pdffile']:
                        #     template ='assessment/reportviewthirdsss.html'
                        #     context = {'form':form,'varerr':varerr,'replist':replist,'school':school,'term':term,'stuno':stuno}
                        #     return render_to_pdf(template, context)
                        # else:
                        return render_to_response('assessment/reportthirdsss.html',
                            {'varerr':varerr,'replist':replist,
                            'annual_class_avg':locale.format("%.1f",annual_class_avg,grouping=True),
                            'school':school,'date':date,'term':term,'next':ntb})


                    elif klass[0] == 'N' or klass[0] == 'C' or klass[0] == 'L':
                        # if form.cleaned_data['pdffile']:
                        #     template ='assessment/reportnviewthird.html'
                        #     context = {'form':form,'varerr':varerr,'replist':replist,'school':school,'term':term,'stuno':stuno,'classavg':locale.format("%.2f",clavg,grouping=True)}
                        #     return render_to_pdf(template, context)
                        # else:
                        return render_to_response('assessment/reportnthirde.html',{'form':form,'varerr':varerr,'replist':replist,'date':date,'school':school,'term':term,'stuno':stuno,'classavg':locale.format("%.2f",clavg,grouping=True)})

                    else:
                        # if form.cleaned_data['pdffile']:
                        #     template ='assessment/reportviewthird.html'
                        #     context = {'form':form,'varerr':varerr,'replist':replist,'school':school,'term':term,'stuno':stuno,'classavg':locale.format("%.2f",clavg,grouping=True)}
                        #     return render_to_pdf(template, context)
                        # else:
                        return render_to_response('assessment/reportthird.html',
                            {'varerr':varerr,
                            'varuser':varuser,
                            'replist':replist,
                            'school':school,
                            'date':date,
                            'term':term,
                            'annual_class_avg':locale.format("%.1f",annual_class_avg,grouping=True),
                            'next':ntb})

        else:
            form = reportsheetform()
            if klassteacher == 1:
                return render_to_response('assessment/report.html',{'varuser':varuser,'form':form,'varerr':varerr})

            elif uenter==True:
                return render_to_response('assessment/reportadmin.html',{'varuser':varuser,'form':form,'varerr':varerr})

    else:
        return HttpResponseRedirect('/login/')




#***********************************************treating MID-TERM Report ****************************


#*****************************************************************************************************
def broadsheet(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.createuser
        if uenter is False :
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails =''
        school = get_object_or_404(School, pk=1)
        if request.method == 'POST':
            form = broadsheetform(request.POST)
            if form.is_valid():
                session = form.cleaned_data['session']
                klass = form.cleaned_data['klass']
                term = form.cleaned_data['term']
                arm = form.cleaned_data['arm']
                y1,y2 =session.split('/')
                filename=klass+ arm+y2+'.xls'
                #***********************************************getting the subjects
                if arm=='SCIENCE':
                    category='Science'

                elif arm == 'ART':
                    category='Art'

                elif arm == 'COMMERCIAL':
                    category='Commercial'
                else:
                    category='JS'

                k= Subject.objects.filter(category=category).order_by('num')


                subjdic = {}

                for sub in k:
                    jk = {sub.subject:sub.subject}
                    subjdic.update(jk)

                sublist = subjdic.keys() #subject list

                #print 'the subject list :',sublist
                #*************************************************************************

                if klass.startswith('S'):


                    ll = bsheetforsa(term,session,klass,arm)




                    response = HttpResponse(mimetype="application/ms-excel")


                    response['Content-Disposition'] = 'attachment; filename= "{}"'.format(filename)


                    wb = xlwt.Workbook()
                    ws = wb.add_sheet('broadsheet')
                    ws.write(0, 28, school.name)
                    ws.write(1, 28, school.address)
                    ws.write(2, 28, '%s %s %s Term Broad Sheet for %s Session' %(klass,arm, term, session) )


                    if term == 'First':

                        df = ['CA','EXAM','TOTAL']
                        b= 2
                        v = 3
                        for p in sublist:
                           ws.write(3, v, p)
                           v += 3
                           for py in df:
                               ws.write(4, b, py)
                               b += 1


                        ws.write(4,0,'Admission No')
                        ws.write(4,1,'Student Name')


                        ws.write(4, v, 'GRADE')
                        v += 1
                        k = 5
                        for jd in ll:

                           kp=2
                           pp=3
                           c = 4
                           ws.write(k, 0, jd['admno'])
                           ws.write(k, 1, jd['stname'])


                           for q in sublist:
                               ws.write(k, kp, jd['tca'][q])
                               kp += 3

                               ws.write(k, pp, jd['texam'][q])
                               pp += 3

                               ws.write(k, c, jd['end_term_score'][q])
                               c += 3

                           c=c-1

                           ws.write(k, c, jd['grade'])
                           k += 1


                        wb.save(response)

                    elif term == 'Second':
                        df = ['1st','CA','EXAM','AVE']

                        b= 2
                        v = 3
                        g=4
                        for p in sublist:
                           ws.write(3, v, p)
                           v += 4
                           for py in df:
                               ws.write(4, b, py)
                               b += 1


                        ws.write(4,0,'Admission No')
                        ws.write(4,1,'Student Name')

                        ws.write(4, v, 'TOTAL')
                        v += 1
                        ws.write(4, v, 'AVG')
                        v += 1
                        ws.write(4, v, 'POSITION')

                        v += 1
                        ws.write(4, v, 'GRADE')



                        k = 5
                        for jd in ll:

                           kp=2
                           pp=3
                           c = 4
                           fg=5
                           qf=6
                           RE=7


                           ws.write(k, 0, jd['studentlist']['admno'])
                           ws.write(k, 1, jd['studentlist']['stname'])

                           for q in sublist:
                               ws.write(k, kp, jd['studentlist']['first_term'][q])
                               kp += 4

                               ws.write(k, pp, jd['studentlist']['tca'][q])
                               pp += 4

                               ws.write(k, c, jd['studentlist']['texam'][q])
                               c += 4

                               ws.write(k, fg, jd['studentlist']['averages'][q])
                               fg += 4


                           c=c-1

                           ws.write(k, c, jd['studentlist']['totalscore'])
                           c += 1


                           ws.write(k, c, '%.2f'%jd['studentlist']['avgscore'])
                           c += 1


                           ws.write(k, c, jd['pos'])
                           c += 1

                           ws.write(k, c, jd['studentlist']['grade'])
                           k += 1







                        wb.save(response)

                    elif term == 'Third':

                        df = ['1st','2nd','CA','EXAM','AVE']
                        b= 2
                        v = 3
                        g=4
                        for p in sublist:
                           ws.write(3, v, p)
                           v += 5
                           for py in df:
                               ws.write(4, b, py)
                               b += 1


                        ws.write(4,0,'Admission No')
                        ws.write(4,1,'Student Name')



                        ws.write(3, v, 'TOTAL')
                        v += 1
                        ws.write(3, v, 'AVG')
                        v += 1
                        ws.write(3, v, 'POSITION')

                        v += 1
                        ws.write(3, v, 'GRADE')

                        k = 5

                        for jd in ll:

                           kp=2
                           pp=3
                           c = 4
                           ff=5
                           qf=6
                           RE=7
                           ws.write(k, 0, jd['studentlist']['admno'])
                           ws.write(k, 1, jd['studentlist']['stname'])

                           for q in sublist:
                               ws.write(k, kp, jd['studentlist']['first_term'][q])
                               kp += 5

                               ws.write(k, pp, jd['studentlist']['second_term'][q])
                               pp += 5

                               ws.write(k, c, jd['studentlist']['tca'][q])
                               c += 5

                               ws.write(k, ff, jd['studentlist']['texam'][q])
                               ff += 5
                               ws.write(k, qf, jd['studentlist']['annual'][q])
                               qf += 5

                           c=c-1

                           ws.write(k, c, jd['studentlist']['totalscore'])
                           c += 1

                           ws.write(k, c, '%.2f'%jd['studentlist']['avgscore'])
                           c += 1

                           ws.write(k, c, jd['pos'])
                           c += 1
                           ws.write(k, c, jd['studentlist']['grade'])
                           k += 1


                    wb.save(response)
                    return response

                else: #for JS Students

                   ll = matola(term,session,klass,arm,category)
                   response = HttpResponse(mimetype="application/ms-excel")

                   response['Content-Disposition'] = 'attachment; filename= "{}"'.format(filename)


                   wb = xlwt.Workbook()
                   ws = wb.add_sheet('broadsheet')
                   ws.write(0, 35, school.name)
                   ws.write(1, 35, school.address)
                   ws.write(2, 35, '%s %s %s Term Broad Sheet for %s Session' %(klass,arm, term, session) )



                   if term == 'First':

                       df = ['CA','EXAM','TOTAL']
                       b= 2
                       v = 3
                       for p in sublist:
                           ws.write(3, v, p)
                           v += 3
                           for py in df:
                               ws.write(4, b, py)
                               b += 1


                       ws.write(4,0,'Admission No')
                       ws.write(4,1,'Student Name')


                       ws.write(4, v, 'TOTAL SCORE')
                       v += 1
                       ws.write(4, v, 'AVERAGE SCORE')
                       v += 1
                       ws.write(4, v, 'POSITION')


                       k = 5
                       for jd in ll:

                           kp=2
                           pp=3
                           c = 4
                           ws.write(k, 0, jd['studentlist']['admno'])
                           ws.write(k, 1, jd['studentlist']['stname'])


                           for q in sublist:
                               ws.write(k, kp, jd['studentlist']['tca'][q])
                               kp += 3

                               ws.write(k, pp, jd['studentlist']['texam'][q])
                               pp += 3

                               ws.write(k, c, jd['studentlist']['end_term_score'][q])
                               c += 3

                           c=c-1

                           ws.write(k, c, jd['studentlist']['totalscore'])
                           c += 1


                           ws.write(k, c, '%.2f'%jd['studentlist']['avgscore'])
                           c += 1


                           ws.write(k, c, jd['pos'])
                           k += 1


                   elif term == 'Second':

                       df = ['1st','CA','EXAM','AVE']
                       b= 2
                       v = 3
                       g=4
                       for p in sublist:
                           ws.write(3, v, p)
                           v += 4
                           for py in df:
                               ws.write(4, b, py)
                               b += 1


                       ws.write(4,0,'Admission No')
                       ws.write(4,1,'Student Name')


                       ws.write(4, v, 'TOTAL')
                       v += 1
                       ws.write(4, v, 'AVG')
                       v += 1
                       ws.write(4, v, 'POSITION')

                       v += 1
                       ws.write(4, v, 'GRADE')

                       # v += 1
                       # ws.write(4, v, 'Remarks')
                       k = 5
                       for jd in ll:

                           kp=2
                           pp=3
                           c = 4
                           ff=5
                           qf=6
                           RE=7

                           ws.write(k, 0, jd['studentlist']['admno'])
                           ws.write(k, 1, jd['studentlist']['stname'])

                           for q in sublist:
                               ws.write(k, kp, jd['studentlist']['first_term'][q])
                               kp += 4

                               ws.write(k, pp, jd['studentlist']['tca'][q])
                               pp += 4

                               ws.write(k, c, jd['studentlist']['texam'][q])
                               c += 4

                               ws.write(k, ff, jd['studentlist']['averages'][q])
                               ff += 4

                           c=c-1

                           ws.write(k, c, jd['studentlist']['totalscore'])
                           c += 1


                           ws.write(k, c, '%.2f'%jd['studentlist']['avgscore'])
                           c += 1


                           ws.write(k, c, jd['pos'])
                           c += 1

                           ws.write(k, c, jd['studentlist']['grade'])
                           k += 1



                   elif term == 'Third':


                       df = ['1st T','2nd T','CA','EXAM','AVE']


                       b= 2
                       v = 3
                       g=4
                       for p in sublist:
                           ws.write(3, v, p)
                           v += 5
                           for py in df:
                               ws.write(4, b, py)
                               b += 1


                       ws.write(4,0,'Admission No')
                       ws.write(4,1,'Student Name')


                       ws.write(3, v, 'TOTAL')
                       v += 1
                       ws.write(3, v, 'AVG')
                       v += 1
                       ws.write(3, v, 'POSITION')

                       v += 1
                       ws.write(3, v, 'GRADE')

                       k = 5
                       for jd in ll:

                           kp=2
                           pp=3
                           c = 4
                           ff=5
                           qf=6
                           RE=7
                           ws.write(k, 0, jd['studentlist']['admno'])
                           ws.write(k, 1, jd['studentlist']['stname'])

                           for q in sublist:
                               ws.write(k, kp, jd['studentlist']['first_term'][q])
                               kp += 5

                               ws.write(k, pp, jd['studentlist']['second_term'][q])
                               pp += 5

                               ws.write(k, c, jd['studentlist']['tca'][q])
                               c += 5

                               ws.write(k, ff, jd['studentlist']['texam'][q])
                               ff += 5
                               ws.write(k, qf, jd['studentlist']['annual'][q])
                               qf += 5

                           c=c-1

                           ws.write(k, c, jd['studentlist']['totalscore'])
                           c += 1

                           ws.write(k, c, '%.2f'%jd['studentlist']['avgscore'])
                           c += 1

                           ws.write(k, c, jd['pos'])
                           c += 1
                           ws.write(k, c, jd['studentlist']['grade'])
                           k += 1


                   wb.save(response)
                return response


        else:
            form = broadsheetform()
        return render_to_response('assessment/broadsheet.html',{'varuser':varuser,'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')
#********************************************************Mid Term Broad Sheet *****************************************
def mid_term_broadsheet(request):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        uenter = user.reportsheet
        if uenter is False :
            return HttpResponseRedirect('/reportsheet/access-denied/')
        varerr =''
        getdetails =''
        school = get_object_or_404(School, pk=1)
        if request.method == 'POST':
            form = broadsheetform(request.POST)
            if form.is_valid():
                session = form.cleaned_data['session']
                klass = form.cleaned_data['klass']
                term = form.cleaned_data['term']
                #***********************************************getting the subjects
                if klass.startswith('J'):
                    k= Subject.objects.filter(category='JS').order_by('num')
                elif klass.startswith('Y'):
                    k= Subject.objects.filter(category='Year').order_by('num')
                else:
                    k= Subject.objects.all().exclude(category='Year').exclude(category='JS').order_by('num')
                subjdic = {}
                for sub in k:
                    jk = {sub.subject:sub.subject}
                    subjdic.update(jk)
                sublist = subjdic.keys()
                #print 'the subject list :',sublist
                #*************************************************************************
                if klass.startswith('S'):
                    ll = mid_term_bsheetfors(term,session,klass)
                    response = HttpResponse(mimetype="application/ms-excel")
                    response['Content-Disposition'] = 'attachment; filename=broadsheet.xls'
                    wb = xlwt.Workbook()
                    ws = wb.add_sheet('broadsheet')
                    ws.write(0, 2, school.name)
                    ws.write(1, 2, school.address)
                    ws.write(2, 2, '%s %s Term Broad Sheet for %s Session' %(klass,term, session) )
                    v = 2
                    ws.write(3,0,'Admission No')
                    ws.write(3,1,'Student Name')
                    for p in sublist:
                        ws.write(3, v, p)
                        v += 1
                    ws.write(3, v, 'GRADE')
                    k = 4
                    for jd in ll:
                       c = 2
                       ws.write(k, 0, jd['admno'])
                       ws.write(k, 1, jd['stname'])
                       for q in sublist:
                           ws.write(k, c, jd['subjects'][q])
                           c += 1
                       ws.write(k, c, jd['grade'])
                       k += 1
                    wb.save(response)
                    return response
                else:
                   ll = mid_term_bsheetforj(term,session,klass)
                   response = HttpResponse(mimetype="application/ms-excel")
                   response['Content-Disposition'] = 'attachment; filename=broadsheet.xls'
                   wb = xlwt.Workbook()
                   ws = wb.add_sheet('broadsheet')
                   ws.write(0, 2, school.name)
                   ws.write(1, 2, school.address)
                   ws.write(2, 2, '%s %s Term Broad Sheet for %s Session' %(klass,term, session) )
                   v = 2
                   ws.write(3,0,'Admission No')
                   ws.write(3,1,'Student Name')
                   for p in sublist:
                       ws.write(3, v, p)
                       v += 1
                   ws.write(3, v, 'TOTAL SCORE')
                   v += 1
                   ws.write(3, v, 'AVERAGE SCORE')
                   v += 1
                   ws.write(3, v, 'POSITION')
                   k = 4
                   for jd in ll:
                       c = 2
                       ws.write(k, 0, jd['studentlist']['admno'])
                       ws.write(k, 1, jd['studentlist']['stname'])
                       for q in sublist:
                           ws.write(k, c, jd['studentlist']['subjects'][q])
                           c += 1
                       ws.write(k, c, jd['studentlist']['totalscore'])
                       c += 1
                       ws.write(k, c, '%.2f'%jd['studentlist']['avgscore'])
                       c += 1
                       ws.write(k, c, jd['pos'])
                       k += 1
                   wb.save(response)
                   return response
                return render_to_response('assessment/midtermbroadsheet.html',{'form':form,'varerr':varerr})
                        #end of position
        else:
            form = broadsheetform()
        return render_to_response('assessment/midtermbroadsheet.html',{'form':form,'varerr':varerr})
    else:
        return HttpResponseRedirect('/login/')



#*****************************************Taking Care Of Returning function for primary School**************************
def primary_url(request,session1,klass1,arm1,name1,term1):
        pry = ''
        for j in appused.objects.all():
            pry = j.primary
        if pry is True :
            pass
        else:
            return HttpResponseRedirect('/reportsheet/access-denied/')
        session = str(session1).replace('j','/')
        klass = str(klass1).replace('k',' ')
        arm = str(arm1).replace('k',' ')
        name11 = str(name1).replace('z',' ')
        fname2 = name11.replace('i','-')
        name  = fname2.replace('u',"'")
        term = str(term1).replace('0',' ')
        getdetails = ''
        getstu = Student.objects.get(admitted_class = klass,admitted_arm=arm,admitted_session = session,fullname = name)
        if StudentAcademicRecord.objects.filter(student = getstu,term = term):
            comm = StudentAcademicRecord.objects.get(student = getstu,term = term)
            getdetails = SubjectScore.objects.filter(session = session,klass = klass, arm = arm,term = term,academic_rec = comm).order_by('num')
        return render_to_response('assessment/subjectpry1.html',{'getdetails':getdetails,'session':session,'klass':klass,'arm':arm , 'd':getstu})

#*****************************************Taking Care Of Returning function for Secondary School**************************
def secondary_url(request,session1,klass1,arm1,name1,term1,grp,rep):
    varuser = request.session['userid']
    sec = ''

    staff = userprofile.objects.get(username=varuser,status='ACTIVE')

    ccc = ClassTeacher.objects.filter(teachername = varuser)
    sss = subjectteacher.objects.filter(teachername = varuser)

    for j in appused.objects.all():
        sec = j.secondary
    if sec is True :
        pass
    else:
        return HttpResponseRedirect('/reportsheet/access-denied/')


    session = str(session1).replace('j','/')
    klass = str(klass1).replace('k',' ')
    arm = str(arm1).replace('k',' ')
    grp = str(grp).replace('m',' ')
    grp1 = str(grp).replace(' ','m')
    subject = str(name1).replace('k',' ')
    term = str(term1).replace('0',' ')
    rep=str(rep).replace('p',' ')
    stlist = []

    if grp =='ALL':

        for j in Student.objects.filter(admitted_session = session,admitted_class = klass,admitted_arm = arm,gone = False).order_by('fullname'):
            if StudentAcademicRecord.objects.filter(student = j,session = session,term = term):
                st = StudentAcademicRecord.objects.get(student = j,session = session,term = term)
                if SubjectScore.objects.filter(academic_rec = st,klass = klass,subject = subject,session = session,arm=arm,term =term):
                    gs = SubjectScore.objects.get(academic_rec = st,
                        klass = klass,
                        subject = subject,
                        session = session,
                        arm=arm,
                        term =term)

                    kk = {'id':gs.id,
                    'admissionno':j.admissionno,
                    'fullname':j.fullname,
                    'sex':j.sex,
                    'subject':gs.subject,
                    'term':str(term),
                    'first_ca':gs.first_ca,
                    'second_ca':gs.second_ca,
                    'third_ca':gs.third_ca,
                    'fourth_ca':gs.fourth_ca,
                    'fifth_ca':gs.fifth_ca,
                    'sixth_ca':gs.sixth_ca,
                    'exam_score':gs.end_term_score}
                    stlist.append(kk)
                else:
                    pass

        if rep == 'Mid term':
            # if klass == 'JS 1' or klass == 'SS 1':
            if ccc.count()> 0:
                return render_to_response('assessment/casecond_cl.htm',{'varuser':varuser,'data':stlist,'session':session,'klass':klass,'arm':arm,'subject':subject,'session1':session1,'klass1':klass1,'arm1':arm1,'name1':name1,'term1':term1,'rep':rep})
            else:
                return render_to_response('assessment/casecond_t.htm',{'varuser':varuser,'data':stlist,'session':session,'klass':klass,'arm':arm,'subject':subject,'session1':session1,'klass1':klass1,'arm1':arm1,'name1':name1,'term1':term1,'rep':rep})
                # return render_to_response('assessment/caredirect.htm',{'varuser':varuser,'data':stlist,'session':session,'klass':klass,'arm':arm,'subject':subject,'session1':session1,'klass1':klass1,'arm1':arm1,'name1':name1,'term1':term1})
        elif rep== 'End term':
            if ccc.count()>0:
                return render_to_response('assessment/caredirect_cl.htm',{'varuser':varuser,'data':stlist,'session':session,'klass':klass,'arm':arm,'subject':subject,'session1':session1,'klass1':klass1,'arm1':arm1,'name1':name1,'term1':term1,'rep':rep})
            else:
                return render_to_response('assessment/caredirect_t.htm',{'varuser':varuser,'data':stlist,'session':session,'klass':klass,'arm':arm,'subject':subject,'session1':session1,'klass1':klass1,'arm1':arm1,'name1':name1,'term1':term1,'rep':rep})

    else:

        for j in Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False).order_by('fullname'):
            if StudentAcademicRecord.objects.filter(student = j,session = session,term = term):
                st = StudentAcademicRecord.objects.get(student = j,session = session,term = term)
                if SubjectScore.objects.filter(academic_rec = st,klass = klass,subject = subject,session = session,subject_group=grp,term =term):
                    gs = SubjectScore.objects.get(academic_rec = st,
                        klass = klass,
                        subject = subject,
                        session = session,
                        term =term)

                    kk = {'id':gs.id,
                    'admissionno':j.admissionno,
                    'arm':gs.arm,
                    'fullname':j.fullname,
                    'sex':j.sex,
                    'subject':gs.subject,
                    'term':str(term),
                    'first_ca':gs.first_ca,
                    'second_ca':gs.second_ca,
                    'third_ca':gs.third_ca,
                    'fourth_ca':gs.fourth_ca,
                    'fifth_ca':gs.fifth_ca,
                    'sixth_ca':gs.sixth_ca,
                    'exam_score':gs.end_term_score}
                    stlist.append(kk)

        if rep =='Mid term':
            # if klass == 'JS 1' or klass1 == 'SS 1':
                return render_to_response('assessment/grpbased.html',{'grp1':grp,'varuser':varuser,'data':stlist,'session':session,'klass':klass,'subject':subject,'session1':session1,'klass1':klass1,'grp':grp1,'name1':name1,'term1':term1})
            # else:
                # return render_to_response('assessment/caredirect.htm',{'varuser':varuser,'data':stlist,'session':session,'klass':klass,'arm':arm,'subject':subject,'session1':session1,'klass1':klass1,'arm1':arm1,'name1':name1,'term1':term1})
        else:
            return render_to_response('assessment/casecond.htm',{'varuser':varuser,'data':stlist,'session':session,'klass':klass,'arm':arm,'subject':subject,'session1':session1,'klass1':klass1,'arm1':arm1,'name1':name1,'term1':term1})





#*****************************************Printing Secondary School Teacher Report**************************

def secondary_teacher_report(request,session1,klass1,arm1,name1,reporttype,term1):
    if  "userid" in request.session:
        varuser = request.session['userid']
        user = userprofile.objects.get(username = varuser)
        session = str(session1).replace('j','/')
        klass = str(klass1).replace('k',' ')
        arm = str(arm1).replace('m',' ')
        subject = str(name1).replace('k',' ')
        term = str(term1).replace('0',' ')
        reporttype = str(reporttype).replace('w',' ')
        stlist = []
        school = get_object_or_404(School, pk=1)

        try:
            Arm.objects.get(arm=arm)
            for j in Student.objects.filter(admitted_session = session,
                admitted_class = klass,
                admitted_arm = arm,
                gone = False).order_by('fullname'):


                if StudentAcademicRecord.objects.filter(student = j,session = session,term = term):
                    st = StudentAcademicRecord.objects.get(student = j,session = session,term = term)
                    if SubjectScore.objects.filter(academic_rec = st,klass = klass,subject = subject,session = session,arm=arm,term =term):

                        gs = SubjectScore.objects.get(academic_rec = st,
                            klass = klass,
                            subject = subject,
                            session = session,
                            arm=arm,
                            term =term)

                        kk = {'id':gs.id,
                        'arm':j.admitted_arm,
                        'klass':j.admitted_class,
                        'admissionno':j.admissionno,
                        'fullname':j.fullname,
                        'subject':gs.subject,
                        'term':str(term),
                        'first_ca':gs.first_ca,
                        'second_ca':gs.second_ca,
                        'third_ca':gs.third_ca,
                        'unified_test':gs.fifth_ca,
                        'mid_term':gs.mid_term_score,
                        'termscore':gs.end_term_score,
                        'remark':gs.grade,
                        'position':gs.subposition}
                        stlist.append(kk)
        except:
            for j in Student.objects.filter(admitted_session = session,
                admitted_class = klass,gone = False).order_by('fullname'):
                if StudentAcademicRecord.objects.filter(student = j,session = session,term = term):
                    st = StudentAcademicRecord.objects.get(student = j,session = session,term = term)
                    if SubjectScore.objects.filter(academic_rec = st,klass = st.klass,subject = subject,session = session,subject_group=arm,term =term):
                        gs = SubjectScore.objects.get(academic_rec = st,
                            klass = st.klass,
                            subject = subject,
                            session = session,
                            subject_group=arm,
                            term =term)

                        kk = {'arm1':j.admitted_arm,
                        'klass':j.admitted_class,
                        'id':gs.id,
                        'admissionno':j.admissionno,
                        'fullname':j.fullname,
                        'sex':j.sex,
                        'subject':gs.subject,
                        'term':str(term),
                        'first_ca':gs.first_ca,
                        'unified_test':gs.unified_test,
                        'second_ca':gs.second_ca,
                        'third_ca':gs.third_ca,
                        'mid_term':gs.mid_term_score,
                        'termscore':gs.end_term_score,
                        'remark':gs.grade,
                        'position':gs.subposition}

                        stlist.append(kk)

        if reporttype == "Mid term":
            return render_to_response('assessment/printcamid.html',{'data':stlist,'name1':name1,'session':session,'klass':klass,'arm':arm,'subject':subject,'term':term,'teacher':str(user.staffname).title(),'school':school})
        else:
            return render_to_response('assessment/printca.htm',{'data':stlist,'name1':name1,'session':session,'klass':klass,'arm':arm,'subject':subject,'term':term,'teacher':str(user.staffname).title(),'school':school})


    else:
        return HttpResponseRedirect('/login/')
