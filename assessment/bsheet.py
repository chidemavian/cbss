from academics.models import *
from academics.utils import *
from setup.models import *
from assessment.getordinal import *
import locale
locale.setlocale(locale.LC_ALL,'')


def bsheetforj(term,session,klass):
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
    stulist = []
    subavg = {}
    gavglist = []
    if term == 'Third':
        stuinfo = Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False)
        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,session = session,term = term)
            getdic = {}
            totscore = 0
            tosub = 0
            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,klass = klass,session = session,subject = js)
                    u = {js:totsubject.annual_avg}
                    totscore += totsubject.annual_avg
                    tosub += 1
                getdic.update(u)
            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub
            l ={'stname':j.fullname,'admno':j.admissionno,'totalscore':totscore,'avgscore':avgscore,'subjects':getdic}
            stulist.append(l)
            ka = {avgscore:avgscore}
            subavg.update(ka)
            gavglist.append(avgscore)
    else:
        stuinfo = Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False)
        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,session = session,term = term)
            getdic = {}
            totscore = 0
            tosub = 0
            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,klass = klass,session = session,subject = js)
                    u = {js:totsubject.end_term_score}
                    totscore += totsubject.end_term_score
                    tosub += 1
                getdic.update(u)
            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub
            l ={'stname':j.fullname,'admno':j.admissionno,'totalscore':totscore,'avgscore':avgscore,'subjects':getdic}
            stulist.append(l)
            ka = {avgscore:avgscore}
            subavg.update(ka)
            gavglist.append(avgscore)
    avglist = subavg.keys()
    avglist.sort(reverse=True)
    n = 1
    #print 'old list',stuperc,'new list',flist
    finallist = []
    for d in avglist:
        pos = ordinal(n)
        for stl in stulist:
            if stl['avgscore'] == d:
                jl = {'studentlist':stl,'pos':pos}
                finallist.append(jl)
        j = gavglist.count(d)
        n += j
    return finallist


def bsheetforja(term,session,klass,arm):
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
    stulist = []
    subavg = {}
    gavglist = []
    if term == 'Third':
        stuinfo = Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False, admitted_arm=arm)
        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,session = session,term = term)
            getdic = {}
            totscore = 0
            tosub = 0
            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,klass = klass,session = session,subject = js)
                    u = {js:totsubject.annual_avg}
                    totscore += totsubject.annual_avg
                    tosub += 1
                getdic.update(u)
            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub
            l ={'stname':j.fullname,'admno':j.admissionno,'totalscore':totscore,'avgscore':avgscore,'subjects':getdic}
            stulist.append(l)
            ka = {avgscore:avgscore}
            subavg.update(ka)
            gavglist.append(avgscore)
    else:
        stuinfo = Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False, admitted_arm=arm)
        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,session = session,term = term)
            getdic = {}
            totscore = 0
            tosub = 0
            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,klass = klass,session = session,subject = js)
                    u = {js:totsubject.end_term_score}
                    totscore += int(totsubject.end_term_score)
                    tosub += 1
                getdic.update(u)
            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub
            l ={'stname':j.fullname,'admno':j.admissionno,'totalscore':totscore,'avgscore':avgscore,'subjects':getdic}
            stulist.append(l)
            ka = {avgscore:avgscore}
            subavg.update(ka)
            gavglist.append(avgscore)
    avglist = subavg.keys()
    avglist.sort(reverse=True)
    n = 1
    #print 'old list',stuperc,'new list',flist
    finallist = []
    for d in avglist:
        pos = ordinal(n)
        for stl in stulist:
            if stl['avgscore'] == d:
                jl = {'studentlist':stl,'pos':pos}
                finallist.append(jl)
        j = gavglist.count(d)
        n += j
    return finallist




def bsheetfors(term,session,klass):
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
    stulist = []
    if term == 'Third':
        stuinfo = Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False)
        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,session = session,term = term)
            getdic = {}
            da = 0
            db = 0
            dc = 0
            dd = 0
            de = 0
            df = 0
            stgrade = ''
            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,klass = klass,session = session,subject = js)
                    u = {js:totsubject.annual_avg}
                    g = totsubject.grade
                    if g[0] == 'A':
                        da += 1
                    elif g[0] == 'B':
                        db += 1
                    elif  g[0] == 'C':
                        dc += 1
                    elif g[0] == 'D':
                        dd += 1
                    elif  g[0] == 'E':
                       de += 1
                    else:
                        df +=1
                stgrade = str(da) +'A,'+str(db)+'B,'+str(dc)+'C,'+str(dd)+'D,'+str(de)+'E,'+str(df)+'F'
                getdic.update(u)
            l ={'stname':j.fullname,'admno':j.admissionno,'grade':stgrade,'subjects':getdic}
            stulist.append(l)
    else:
        stuinfo = Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False)
        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,session = session,term = term)
            getdic = {}
            da = 0
            db = 0
            dc = 0
            dd = 0
            de = 0
            df = 0
            stgrade = ''
            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,klass = klass,session = session,subject = js)
                    u = {js:totsubject.end_term_score}
                    g = totsubject.grade
                    if g[0] == 'A':
                        da += 1
                    elif g[0] == 'B':
                        db += 1
                    elif  g[0] == 'C':
                        dc += 1
                    elif g[0] == 'D':
                        dd += 1
                    elif  g[0] == 'E':
                        de += 1
                    else:
                        df +=1
                stgrade = str(da) +'A,'+str(db)+'B,'+str(dc)+'C,'+str(dd)+'D,'+str(de)+'E,'+str(df)+'F'
                getdic.update(u)
            l ={'stname':j.fullname,'admno':j.admissionno,'grade':stgrade,'subjects':getdic}
            stulist.append(l)
    return stulist


def matola(term,session,klass,arm,category):

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
    sublist = subjdic.keys() #actual subject


    stulist = [] #student portfolio
    subavg = {} #subject average

    gavglist = []
    if term == 'Third':
        stuinfo = Student.objects.filter(admitted_session = session,
            admitted_class = klass,
            gone = False,
            third_term=1,
            admitted_arm=arm)

        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = term)

            acaderec_first = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = 'First')


            acaderec_second = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = 'Second')

            acaderec_first_count = acaderec_first.count()
            acaderec_second_count = acaderec_second.count()



            da = 0
            db = 0
            dc = 0
            dd = 0
            de = 0
            df = 0






            c={}
            e={}
            anv={}
            ftp={}
            stp={}


            getdic = {}
            totscore = 0
            tosub = 0

            stgrade = ''


            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                    u2 = {js:0}
                    ca = {js:0}
                    exam = {js:0}

                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,
                        klass = klass,
                        session = session,
                        subject = js)

                    ca2 = int(totsubject.third_ca) + int(totsubject.fourth_ca)

                    ca={js:ca2}
                    exam={js:totsubject.sixth_ca}
                    u = {js:totsubject.end_term_score}
                    u2 = {js:totsubject.annual_avg}

                    totscore += int(totsubject.end_term_score)
                    tosub += 1

                    g = totsubject.grade
                    if g[0] == 'A':
                        da += 1
                    elif g[0] == 'B':
                        db += 1
                    elif  g[0] == 'C':
                        dc += 1
                    elif g[0] == 'D':
                        dd += 1
                    elif  g[0] == 'E':
                       de += 1
                    else:
                        df +=1


                stgrade = str(da) +'A,'+str(db)+'B,'+str(dc)+'C,'+str(dd)+'D,'+str(de)+'E,'+str(df)+'F'

                getdic.update(u)
                c.update(ca)
                e.update(exam)
                anv.update(u2)

                if acaderec_first_count==0:
                    first_termm = {js:0}

                else:
                    try:
                        fff = SubjectScore.objects.get(academic_rec = acaderec_first ,klass = klass,session = session,subject = js)
                        first_termm = {js:fff.end_term_score}
                    except:
                        first_termm = {js:0}

                ftp.update(first_termm)


                if acaderec_second_count==0:
                    second_termm = {js:0}

                else:
                    try:
                        ffp= SubjectScore.objects.get(academic_rec = acaderec_second ,klass = klass,session = session,subject = js)
                        second_termm = {js:ffp.end_term_score}
                    except:
                        second_termm = {js:0}

                stp.update(second_termm)



            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub

            l ={'stname':j.fullname,
                'admno':j.admissionno,
                'grade':stgrade,
                'totalscore':totscore,
                'avgscore':avgscore,
                'end_term_score':getdic,
                'tca':c,
                'first_term':ftp,
                'second_term':stp,
                'annual':anv,
                'texam':e}


            stulist.append(l)


            ka = {avgscore:avgscore}
            subavg.update(ka)
            gavglist.append(avgscore)


        avglist = subavg.keys()
        avglist.sort(reverse=True)
        n = 1
        #print 'old list',stuperc,'new list',flist
        finallist = []
        for d in avglist:
            pos = ordinal(n)
            for stl in stulist:
                if stl['avgscore'] == d:
                    jl = {'studentlist':stl,'pos':pos}
                    finallist.append(jl)
            j = gavglist.count(d)
            n += j
        return finallist





    elif term == 'Second':
        stuinfo = Student.objects.filter(admitted_session = session,
            admitted_class = klass,
            gone = False,
            second_term=1,
            admitted_arm=arm)

        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = term)

            acaderec_first = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = 'First')

            acaderec_first_count = acaderec_first.count()


            da = 0
            db = 0
            dc = 0
            dd = 0
            de = 0
            df = 0


            getdic = {} #end term score
            c={}
            e={}
            ftp={}
            sub_avv={}

            totscore = 0
            tosub = 0 #total subject offered by a student

            stgrade = ''

            for js in sublist: #subject list

                tottt = SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js)
                if tottt.count() == 0:

                    u = {js:0}
                    ca = {js:0}
                    exam = {js:0}

                else:
                    totsubject = tottt.get()
                    ca2 = int(totsubject.third_ca) + int(totsubject.fourth_ca)


                    ca={js:ca2}
                    exam={js:totsubject.sixth_ca}
                    u = {js:totsubject.end_term_score}

                    totscore += int(totsubject.end_term_score)
                    tosub += 1

                    g = totsubject.grade
                    if g[0] == 'A':
                        da += 1
                    elif g[0] == 'B':
                        db += 1
                    elif  g[0] == 'C':
                        dc += 1
                    elif g[0] == 'D':
                        dd += 1
                    elif  g[0] == 'E':
                       de += 1
                    else:
                        df +=1


                stgrade = str(da) +'A,'+str(db)+'B,'+str(dc)+'C,'+str(dd)+'D,'+str(de)+'E,'+str(df)+'F'



                getdic.update(u)
                c.update(ca)
                e.update(exam)

                if acaderec_first_count==0:
                    first_termm = {js:0}
                else:
                    try:
                        fff = SubjectScore.objects.get(academic_rec = acaderec_first ,klass = klass,session = session,subject = js)
                        first_termm = {js:fff.end_term_score}
                    except:
                        first_termm = {js:0}

                ftp.update(first_termm)

                if acaderec_first_count==0:
                    if tottt.count()==0:
                        sub_avg=0
                    else:
                        sub_avg = totsubject.end_term_score

                else:
                    sub_avg = (int(fff.end_term_score) + int(totsubject.end_term_score ))*0.5



                aa = {js:sub_avg}

                sub_avv.update(aa)



            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub



            l ={'stname':j.fullname,
                'admno':j.admissionno,
                'totalscore':totscore,
                'avgscore':avgscore,
                'grade':stgrade,
                'averages':sub_avv,
                'end_term_score':getdic,
                'tca':c,
                'first_term':ftp,
                'texam':e}

            stulist.append(l)

            ka = {avgscore:avgscore}
            subavg.update(ka)

            gavglist.append(avgscore)

        avglist = subavg.keys()
        avglist.sort(reverse=True)
        n = 1
        #print 'old list',stuperc,'new list',flist
        finallist = []
        for d in avglist:
            pos = ordinal(n)
            for stl in stulist:
                if stl['avgscore'] == d:
                    jl = {'studentlist':stl,'pos':pos}
                    finallist.append(jl)
            j = gavglist.count(d)
            n += j
        return finallist


    elif term == 'First':
        stuinfo = Student.objects.filter(admitted_session = session,
            admitted_class = klass,
            gone = False,
            first_term=1,
            admitted_arm=arm)

        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = term)

            getdic = {} #end term score
            c={}
            e={}

            totscore = 0
            tosub = 0 #total subject offered by a student

            for js in sublist:


                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                    ca = {js:0}
                    exam = {js:0}

                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,
                        klass = klass,
                        session = session,
                        subject = js)

                    ca2 = int(totsubject.third_ca) + int(totsubject.fourth_ca)


                    ca={js:ca2}
                    exam={js:totsubject.sixth_ca}
                    u = {js:totsubject.end_term_score}

                    totscore += int(totsubject.end_term_score)
                    tosub += 1

                getdic.update(u)
                c.update(ca)
                e.update(exam)


            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub


            l ={'stname':j.fullname,
                'admno':j.admissionno,
                'totalscore':totscore,
                'avgscore':avgscore,
                'end_term_score':getdic,
                'tca':c,
                'texam':e}

            stulist.append(l)

            ka = {avgscore:avgscore}
            subavg.update(ka)

            gavglist.append(avgscore)

        avglist = subavg.keys()
        avglist.sort(reverse=True)
        n = 1
        #print 'old list',stuperc,'new list',flist
        finallist = []
        for d in avglist:
            pos = ordinal(n)
            for stl in stulist:
                if stl['avgscore'] == d:
                    jl = {'studentlist':stl,'pos':pos}
                    finallist.append(jl)
            j = gavglist.count(d)
            n += j
        return finallist


def bsheetforsa(term,session,klass,arm):
    if arm=='SCIENCE':
        category='Science'

    elif arm == 'ART':
        category='Art'

    elif arm == 'COMMERCIAL':
        category='Commercial'




    k= Subject.objects.filter(category=category).order_by('num')


    subjdic = {}
    for sub in k:
        jk = {sub.subject:sub.subject}
        subjdic.update(jk)
    sublist = subjdic.keys()


    stulist = []
    subavg = {} #subject average

    gavglist = []
    if term == 'Third':
        stuinfo = Student.objects.filter(admitted_session = session,
            admitted_class = klass,
            gone=False,
            third_term=1,
            admitted_arm=arm)

        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = term)

            acaderec_first = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = 'First')


            acaderec_second = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = 'Second')

            acaderec_first_count = acaderec_first.count()
            acaderec_second_count = acaderec_second.count()



            da = 0
            db = 0
            dc = 0
            dd = 0
            de = 0
            df = 0






            c={} #ca
            e={} #exam score only
            anv={} #annual average
            ftp={} #first term
            scnd={} #second term


            getdic = {}
            totscore = 0
            tosub = 0

            stgrade = ''


            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                    u2={js:0}
                    ca = {js:0}
                    exam={js:0}

                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,
                        klass = klass,
                        session = session,
                        subject = js)

                    ca2 = int(totsubject.third_ca) + int(totsubject.fourth_ca)

                    ca={js:ca2}
                    exam={js:totsubject.sixth_ca}
                    u = {js:totsubject.end_term_score}
                    u2 = {js:totsubject.annual_avg}

                    totscore += int(totsubject.end_term_score)
                    tosub += 1

                    g = totsubject.grade
                    if g[0] == 'A':
                        da += 1
                    elif g[0] == 'B':
                        db += 1
                    elif  g[0] == 'C':
                        dc += 1
                    elif g[0] == 'D':
                        dd += 1
                    elif  g[0] == 'E':
                       de += 1
                    else:
                        df +=1


                stgrade = str(da) +'A,'+str(db)+'B,'+str(dc)+'C,'+str(dd)+'D,'+str(de)+'E,'+str(df)+'F'

                getdic.update(u)
                c.update(ca)
                e.update(exam)
                anv.update(u2) #annual avg

                if acaderec_first_count==0:
                    first_termm = {js:0}

                else:
                    try:
                        fff = SubjectScore.objects.get(academic_rec = acaderec_first ,
                            klass = klass,
                            session = session,
                            subject = js)

                        first_termm = {js:fff.end_term_score}
                    except:
                        first_termm = {js:0}

                ftp.update(first_termm)


                if acaderec_second_count==0:
                    second_termm = {js:0}

                else:
                    try:
                        sss = SubjectScore.objects.get(academic_rec = acaderec_second ,
                            klass = klass,
                            session = session,
                            subject = js)

                        second_termm = {js:sss.end_term_score}
                    except:
                        second_termm = {js:0}

                scnd.update(second_termm)


            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub


            l ={'stname':j.fullname,
                'admno':j.admissionno,
                'grade':stgrade,

                'totalscore':totscore,
                'avgscore':avgscore,

                'end_term_score':getdic,
                'tca':c,
                'first_term':ftp,
                'second_term':scnd,
                'annual':anv,
                'texam':e}


            stulist.append(l)



            ka = {avgscore:avgscore}
            subavg.update(ka)
            gavglist.append(avgscore)

        avglist = subavg.keys()
        avglist.sort(reverse=True)
        n = 1
        #print 'old list',stuperc,'new list',flist
        finallist = []
        for d in avglist:
            pos = ordinal(n)
            for stl in stulist:
                if stl['avgscore'] == d:
                    jl = {'studentlist':stl,'pos':pos}
                    finallist.append(jl)
            j = gavglist.count(d)
            n += j
        return finallist


    elif term == 'Second':
        stuinfo = Student.objects.filter(admitted_session = session,
            admitted_class = klass,
            gone = False,
            second_term=1,
            admitted_arm=arm)

        for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = term)

            acaderec_first = StudentAcademicRecord.objects.filter(student = j,
                session = session,
                term = 'First')

            acaderec_first_count = acaderec_first.count()


            da = 0
            db = 0
            dc = 0
            dd = 0
            de = 0
            df = 0


            getdic = {} #end term score
            c={}
            e={}
            ftp={}
            sub_avv={}

            totscore = 0
            tosub = 0 #total subject offered by a student

            stgrade = ''

            for js in sublist: #subject list

                tottt = SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js)
                if tottt.count() == 0:

                    u = {js:0}
                    ca = {js:0}
                    exam = {js:0}

                else:
                    totsubject = tottt.get()
                    ca2 = int(totsubject.third_ca) + int(totsubject.fourth_ca)


                    ca={js:ca2}
                    exam={js:totsubject.sixth_ca}
                    u = {js:totsubject.end_term_score}

                    totscore += int(totsubject.end_term_score)
                    tosub += 1

                    g = totsubject.grade
                    if g[0] == 'A':
                        da += 1
                    elif g[0] == 'B':
                        db += 1
                    elif  g[0] == 'C':
                        dc += 1
                    elif g[0] == 'D':
                        dd += 1
                    elif  g[0] == 'E':
                       de += 1
                    else:
                        df +=1


                stgrade = str(da) +'A,'+str(db)+'B,'+str(dc)+'C,'+str(dd)+'D,'+str(de)+'E,'+str(df)+'F'



                getdic.update(u)
                c.update(ca)
                e.update(exam)

                if acaderec_first_count==0:
                    first_termm = {js:0}
                else:
                    try:
                        fff = SubjectScore.objects.get(academic_rec = acaderec_first ,klass = klass,session = session,subject = js)
                        first_termm = {js:fff.end_term_score}
                    except:
                        first_termm = {js:0}

                ftp.update(first_termm)

                if acaderec_first_count==0:
                    if tottt.count()==0:
                        sub_avg=0
                    else:
                        sub_avg = totsubject.end_term_score

                else:
                    sub_avg = (int(fff.end_term_score) + int(totsubject.end_term_score ))*0.5



                aa = {js:sub_avg}

                sub_avv.update(aa)



            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub



            l ={'stname':j.fullname,
                'admno':j.admissionno,
                'totalscore':totscore,
                'avgscore':avgscore,
                'grade':stgrade,
                'averages':sub_avv,
                'end_term_score':getdic,
                'tca':c,
                'first_term':ftp,
                'texam':e}

            stulist.append(l)

            ka = {avgscore:avgscore}
            subavg.update(ka)

            gavglist.append(avgscore)

        avglist = subavg.keys()
        avglist.sort(reverse=True)
        n = 1
        #print 'old list',stuperc,'new list',flist
        finallist = []
        for d in avglist:
            pos = ordinal(n)
            for stl in stulist:
                if stl['avgscore'] == d:
                    jl = {'studentlist':stl,'pos':pos}
                    finallist.append(jl)
            j = gavglist.count(d)
            n += j
        return finallist




#***********************************************************Treating mid term broad sheet ***********************
def mid_term_bsheetforj(term,session,klass):
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
    stulist = []
    subavg = {}
    gavglist = []
    stuinfo = Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False)
    submid = 0
    for uuu in Subject.objects.all():
        submid = uuu.ca
        submiddiv = int(submid)/2#divide total CA by 2 e.g if ca = 30 we need 15
    for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,session = session,term = term)
            getdic = {}
            totscore = 0
            tosub = 0
            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,klass = klass,session = session,subject = js)
                    score = totsubject.first_ca
                    totalperc1 = score/submiddiv
                    totalperc = totalperc1 * 100
                    u = {js:locale.format("%.2f",totalperc,grouping=True)}
                    totscore += totalperc
                    tosub += 1
                getdic.update(u)
            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub
            l ={'stname':j.fullname,'admno':j.admissionno,'totalscore':locale.format("%.2f",totscore,grouping=True),'avgscore':avgscore,'subjects':getdic}
            stulist.append(l)
            ka = {avgscore:avgscore}
            subavg.update(ka)
            gavglist.append(avgscore)
    avglist = subavg.keys()
    avglist.sort(reverse=True)
    n = 1
    finallist = []
    for d in avglist:
        pos = ordinal(n)
        for stl in stulist:
            if stl['avgscore'] == d:
                jl = {'studentlist':stl,'pos':pos}
                finallist.append(jl)
        j = gavglist.count(d)
        n += j
    return finallist


def mid_term_bsheetforja(term,session,klass,arm):
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
    stulist = []
    subavg = {}
    gavglist = []
    stuinfo = Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False)
    submid = 0
    for uuu in Subject.objects.all():
        submid = uuu.ca
        submiddiv = int(submid)/2#divide total CA by 2 e.g if ca = 30 we need 15
    for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,session = session,term = term)
            getdic = {}
            totscore = 0
            tosub = 0
            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,klass = klass,session = session,subject = js)
                    score = totsubject.first_ca
                    totalperc1 = score/submiddiv
                    totalperc = totalperc1 * 100
                    u = {js:locale.format("%.2f",totalperc,grouping=True)}
                    totscore += totalperc
                    tosub += 1
                getdic.update(u)
            if tosub == 0:
                avgscore = 0
            else:
                avgscore = totscore/tosub
            l ={'stname':j.fullname,'admno':j.admissionno,'totalscore':locale.format("%.2f",totscore,grouping=True),'avgscore':avgscore,'subjects':getdic}
            stulist.append(l)
            ka = {avgscore:avgscore}
            subavg.update(ka)
            gavglist.append(avgscore)
    avglist = subavg.keys()
    avglist.sort(reverse=True)
    n = 1
    finallist = []
    for d in avglist:
        pos = ordinal(n)
        for stl in stulist:
            if stl['avgscore'] == d:
                jl = {'studentlist':stl,'pos':pos}
                finallist.append(jl)
        j = gavglist.count(d)
        n += j
    return finallist



def mid_term_bsheetfors(term,session,klass):
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
    stulist = []
    stuinfo = Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False)
    submid = 0
    for uuu in Subject.objects.all():
        submid = uuu.ca
        submiddiv = int(submid)/2#divide total CA by 2 e.g if ca = 30 we need 15
    for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,session = session,term = term)
            getdic = {}
            da = 0
            db = 0
            dc = 0
            dd = 0
            de = 0
            df = 0
            stgrade = ''
            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,klass = klass,session = session,subject = js)
                    score = totsubject.first_ca
                    totalperc1 = score/submiddiv
                    totalperc = totalperc1 * 100
                    u = {js:locale.format("%.2f",totalperc,grouping=True)}
                    gr = seniorgrade(totalperc)
                    g = gr['grade']
                    if g == "":
                        df +=1
                    else:
                        if g[0] == 'A':
                            da += 1
                        elif g[0] == 'B':
                            db += 1
                        elif  g[0] == 'C':
                            dc += 1
                        elif g[0] == 'D':
                            dd += 1
                        elif  g[0] == 'E':
                            de += 1
                        else:
                            df +=1
                stgrade = str(da) +'A,'+str(db)+'B,'+str(dc)+'C,'+str(dd)+'D,'+str(de)+'E,'+str(df)+'F'
                getdic.update(u)
            l ={'stname':j.fullname,'admno':j.admissionno,'grade':stgrade,'subjects':getdic}
            stulist.append(l)
    return stulist


def mid_term_bsheetforsa(term,session,klass,arm):
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
    stulist = []
    stuinfo = Student.objects.filter(admitted_session = session,admitted_class = klass,gone = False)
    submid = 0
    for uuu in Subject.objects.all():
        submid = uuu.ca
        submiddiv = int(submid)/2#divide total CA by 2 e.g if ca = 30 we need 15
    for j in stuinfo:
            acaderec = StudentAcademicRecord.objects.filter(student = j,session = session,term = term)
            getdic = {}
            da = 0
            db = 0
            dc = 0
            dd = 0
            de = 0
            df = 0
            stgrade = ''
            for js in sublist:
                if SubjectScore.objects.filter(academic_rec = acaderec,klass = klass,session = session,subject = js).count() == 0:
                    u = {js:0}
                else:
                    totsubject = SubjectScore.objects.get(academic_rec = acaderec,klass = klass,session = session,subject = js)
                    score = totsubject.first_ca
                    totalperc1 = score/submiddiv
                    totalperc = totalperc1 * 100
                    u = {js:locale.format("%.2f",totalperc,grouping=True)}
                    gr = seniorgrade(totalperc)
                    g = gr['grade']
                    if g == "":
                        df +=1
                    else:
                        if g[0] == 'A':
                            da += 1
                        elif g[0] == 'B':
                            db += 1
                        elif  g[0] == 'C':
                            dc += 1
                        elif g[0] == 'D':
                            dd += 1
                        elif  g[0] == 'E':
                            de += 1
                        else:
                            df +=1
                stgrade = str(da) +'A,'+str(db)+'B,'+str(dc)+'C,'+str(dd)+'D,'+str(de)+'E,'+str(df)+'F'
                getdic.update(u)
            l ={'stname':j.fullname,'admno':j.admissionno,'grade':stgrade,'subjects':getdic}
            stulist.append(l)
    return stulist


