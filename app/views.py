from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from app.models import *
import collections
from datetime import datetime
import json
from dejavu import Dejavu
from random import randint
import digest


with open("dejavu.cnf.SAMPLE") as f:
    config = json.load(f)

@login_required
@csrf_protect
def index(request):
    context = {}
    context['today'] = datetime.now()
    context['user_id'] = "1"
    context['class_id'] = "1"
    context['session'] = generate()
    return render(request, 'index.html', context)

@csrf_protect
def student(request):
    context = {}
    context['today'] = datetime.now()
    context['is_mobile'] = request.user_agent.is_mobile
    context['is_chrome'] = request.user_agent.browser.family
    context['session'] = generate()
    family = request.user_agent.browser.family
    if not request.user_agent.is_mobile:
        return render(request, 'desktop_warning.html', context)
    if 'Chrome' not in family and 'Safari' not in family:
        return render(request, 'desktop_warning.html', context)

    return render(request, 'student.html', context)

@login_required
def instructor_input(request):
    user_id = request.META['HTTP_USERID']
    class_id = request.META['HTTP_CLASSID']
    session = request.META['HTTP_SESSIONNAME']
    version = request.META['HTTP_VERSIONNAME']
    djv = Dejavu(config)

    filename = 'media/instructor/instructor_' + user_id +'_' + class_id + '_' + session +'_' + version +'.wav'
    uploadedFile = open(filename, "wb")
    uploadedFile.write(request.body)
    uploadedFile.close()

    c = Classroom.objects.get(id=1)  # hardcoded
    u = User.objects.get(id=1)
    InstructorInbound(user = u, classroom = c, session = session, time_in=datetime.now().replace(tzinfo=None)).save()

    djv.fingerprint_directory("media/instructor/", [".wav"])
    response = djv.db.get_num_fingerprints()
    digest.run()
    return HttpResponse(response)

def student_input(request):
    studentID = request.META['HTTP_STUDENTID']
    session = request.META['HTTP_SESSIONNAME']
    ip = get_client_ip(request)
    ip = ip.replace('.', '-').replace(':', '-')
    class_id =1 #hardcoded
    filename = 'media/student/'+ str(studentID) + '_' + str(class_id) + '_' + session +'_' + ip + '.wav'
    uploadedFile = open(filename, "wb")
    uploadedFile.write(request.body)
    uploadedFile.close()

    c = Classroom.objects.get(id = 1) #hardcoded
    s,created = Student.objects.get_or_create(studentID = studentID)
    StudentInbound(studentID = s, classroom = c, session = session,  time_in=datetime.now().replace(tzinfo=None)).save()

    response = "File received "
    digest.run()
    return HttpResponse(response)

def polling_results(request):
    studentID = request.GET.get('id', None)
    session = request.GET.get('session', None)
    special_poll = request.GET.get('special', None)
    if special_poll == '1':
        digest.run()
        return HttpResponse(json.dumps({'status': 'running digest'}), content_type="application/json")
    if session and student:
        s, c = Student.objects.get_or_create(studentID = studentID)
        a = Attendance.objects.filter(student = s, session=session)
        if a:
            return HttpResponse(json.dumps({'status': a[0].status}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'status': 'pending'}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'status': 'pending'}), content_type="application/json")

@login_required
def instructor_report(request):
    context = {}
    context['today'] = datetime.now()
    t = datetime.now().date()

    a = Attendance.objects.filter(status = 'A', time_in__gte = t)
    absent = []
    for s in a:
        absent.append({'id': s.id, 'studentID': s.student.studentID, 'status': 'Absent'})
    context['absent'] = absent

    cl = ClassList.objects.filter(classroom_id = 1) #hardcoded
    shazam_students = Attendance.objects.filter(time_in__gte = t).values_list('student__studentID', flat=True)
    absent_from_list = []
    for l in cl:
        if l.student.studentID not in shazam_students:
            absent_from_list.append({'id': l.student.id, 'studentID': l.student.studentID, 'status': 'Absent'})
    context['absent_from_list'] = absent_from_list

    #Catch people who use their phones to sign in their friends.
    ips = list(Attendance.objects.filter(time_in__gte=t).values_list('ip', flat=True))
    dups = [item for item, count in collections.Counter(ips).items() if count > 1]

    for ip in dups:
        if ip == 0 or ip == "" : continue
        cheaters = Attendance.objects.filter(time_in__gte=t, ip=ip)
        for cheater in cheaters:
            cheater.status = 'C'
            cheater.save()

    c = Attendance.objects.filter(status='C', time_in__gte=t)
    cheaters = []
    for s in c:
        code = s.ip.replace('-', '')
        cheaters.append({'id': s.id, 'studentID': s.student.studentID, 'status': 'Absent', 'code': code})
    context['cheaters'] = cheaters

    context['no_of_absent_students'] = len(absent) + len(absent_from_list)
    context['no_of_cheaters'] = len(cheaters)
    return render(request, 'instructor_report.html', context)

def student_history(request):
    studentID = request.GET.get('id', None)
    context = {}
    context['today'] = datetime.now()
    s = Student.objects.get(studentID=studentID)
    a = Attendance.objects.filter(student = s).order_by('-id')
    results = []
    for s in a:
        if s.status == 'P': status = "Present"
        elif s.status == 'C': status = "See TA"
        else: status =  "Absent"
        results.append({'studentID': s.student.studentID, 'status': status, 'date': s.time_in})
    context['results'] = results
    return render(request, 'student_history.html', context)

@login_required
def mark_as_present(request):
    response = {}
    data = request.GET.get('id')
    code, id_ = data.split('_')
    if code == 'a':
        a = Attendance.objects.get(id = id_)
        dict_ = json.loads(a.dejavu_log)
        dict_['changed_from'] = a.status
        dict_['changed_to'] = 'P'
        dict_['change_time'] = datetime.now()
        a.dejavu_log = dict_
        a.status = 'P'
        a.save()
        response['status'] = "update attendance"
    elif code == 'c':
        a = Attendance.objects.get(id = id_)
        dict_ = {}
        dict_['changed_from'] = a.status
        dict_['changed_to'] = 'P'
        dict_['change_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        a.dejavu_log += json.dumps(dict_)
        a.status = 'P'
        a.ip = a.ip + "_" + str(generate())  # To avoid being labelled as suscpicious again
        a.save()
        response['status'] = "update attendance to present"
    else:
        s = Student.objects.get(id = id_)
        c = Classroom.objects.get(id = 1) #hardcoded
        a = Attendance()
        a.student = s
        a.classroom = c
        a.status = "P"
        a.session = "0000"
        a.ip = ""
        a.confidence_score = 0
        a.offset = 0
        a.song_name = "None"
        a.offset_seconds = 0
        a.match_time = 0
        a.dejavu_log = json.dumps({"instructor override": True})
        a.time_in = datetime.now()
        a.save()
        response['status'] = "create attendance record"
    response['id'] = data
    return HttpResponse(json.dumps(response), content_type="application/json")

@login_required
def mark_as_absent(request):
    response = {}
    data = request.GET.get('id')
    code, id_ = data.split('_')
    a = Attendance.objects.get(id = id_)
    dict_ =  {}
    dict_['changed_from'] = a.status
    dict_['changed_to'] = 'A'
    dict_['change_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    a.dejavu_log += json.dumps(dict_)
    a.status = 'A'
    a.ip = a.ip + "_" + str(generate()) # To avoid being labelled as suscpicious again
    a.save()
    response['status'] = "update attendance to present"
    response['id'] = data
    return HttpResponse(json.dumps(response), content_type="application/json")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate():
    n = 6
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)