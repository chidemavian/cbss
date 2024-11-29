from academics.models import *
from student.models import *


def classavg(self):
    a = SubjectScore.objects.filter(subject=self.subject, term=self.term,
        session=self.session, klass=self.klass,
        arm=self.arm).aggregate(Avg('end_term_score'))
    kk = a['term_score__avg']
    return kk


def juniorgrade(score):
    if (score >=90) and (score <= 100):
        grade = 'A+'
        remark = 'EXCELLENT'
    elif (score >=75) and (score <= 90.9):
        grade = 'A'
        remark = 'EXCELLENT'
    elif (score >=65) and (score <= 74.9):
        grade = 'B'
        remark = 'VERY GOOD'
    elif (score >=50) and (score <= 64.9):
        grade = 'C'
        remark = 'GOOD'
    elif (score >=45) and (score <= 49.9):
        grade = 'D'
        remark = 'PASS'
    elif (score >=40) and (score <= 44.9):
        grade = 'E'
        remark = 'FAIR'
    elif (score >=0) and (score <= 39.9):
        grade = 'F'
        remark = 'FAIL'
    else:
        grade = 0
        remark ='FAIL'
    return {'remark':remark,'grade':grade}


def seniorgrade(score):
    if (score >=80) and (score <= 100):
        grade = 'A1'
        remark = 'DISTINCTION'
    elif (score >=75) and (score <= 79.99):
        grade = 'B2'
        remark = 'EXCELLENT'
    elif (score >=70) and (score <= 74.99):
        grade = 'B3'
        remark = 'VERY GOOD'
    elif (score >=65) and (score <= 69.99):
        grade = 'C4'
        remark = 'VERY GOOD'
    elif (score >=60) and (score <= 64.99):
        grade = 'C5'
        remark = 'GOOD'
    elif (score >=50) and (score <= 59.99):
        grade = 'C6'
        remark = 'GOOD'
    elif (score >=45) and (score <= 49.99):
        grade = 'D7'
        remark = 'PASS'
    elif (score >=40) and (score <= 44.99):
        grade = 'E8'
        remark = 'FAIR'
    elif (score >=0) and (score <= 39.99):
        grade = 'F9'
        remark = 'FAIL'
    else:
        grade =0
        remark = 'FAIL'
    return {'remark':remark,'grade':grade}




def studentaveragedrader(score):
    if (score >=80) and (score <= 100):
        grade = 'A'
        remark = 'DISTINCTION'
    elif (score >=70) and (score <= 79.99):
        grade = 'B'
        remark = 'VERY GOOD'
    elif (score >=50) and (score <= 69.99):
        grade = 'C'
        remark = 'GOOD'
    elif (score >=45) and (score <= 49.99):
        grade = 'D'
        remark = 'PASS'
    elif (score >=40) and (score <= 44.99):
        grade = 'E'
        remark = 'FAIR'
    elif (score >=0) and (score <= 39.99):
        grade = 'F'
        remark = 'FAIL'
    else:
        grade =0
        remark = 'FAIL'
    return {'remark':remark,'grade':grade}
