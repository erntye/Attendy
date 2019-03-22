#!/usr/bin/env bash
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
import django
django.setup()

from app.models import *
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
import json
from datetime import datetime
#from celery.decorators import task


path = 'media/student/'
with open("dejavu.cnf.SAMPLE") as f:
    config = json.load(f)

def save_record(filename, response):
    if response['confidence'] > 0:
        status = "P"
    else:
        status = "A"

    #To catch users who use recordings or try to submit way past when the instructor has already finished taking attendance
    try:
        last_instructor_inbound = InstructorInbound.objects.filter(clasroom_id = 1).order_by('-id')[0] # hardcoded
        now = datetime.now().replace(tzinfo=None)
        lapse = (now - last_instructor_inbound.time_in.replace(tzinfo=None)).total_seconds()
        if lapse > 60:
            status = 'C'
    except:
        pass

    student_id = filename.split('_')[0]
    ip = filename.split('_')[3].split('.')[0]
    session = filename.split('_')[2].split('.')[0]
    student, created = Student.objects.get_or_create(studentID=student_id)
    c = Classroom.objects.get(id = 1) #hardcoded


    today = datetime.now().date()
    a = Attendance.objects.filter(student = student, time_in__gte = today) #Have only one record per student per day
    if a:
        a = a[0]
        a.status = status
        a.session = session
        a.ip = ip
        a.confidence_score = response['confidence']
        a.offset = response['offset']
        a.song_name = response['song_name']
        a.offset_seconds = response['offset_seconds']
        a.match_time = response['match_time']
        a.dejavu_log = json.dumps(response)
        a.time_in = datetime.now()
        a.save()
    else:
        a = Attendance(student=student,
                       classroom = c,
                       status=status,
                       session = session,
                       ip=ip,
                       confidence_score=response['confidence'],
                       offset=response['offset'],
                       song_name = response['song_name'],
                       offset_seconds=response['offset_seconds'],
                       match_time=response['match_time'],
                       dejavu_log=json.dumps(response),
                       time_in = datetime.now()
                       )
        a.save()

#@task(name='digest')
def run():
    print("Running digest")
    for filename in os.listdir(path):
        print(path + filename)
        djv = Dejavu(config)
        response = djv.recognize(FileRecognizer, path + filename)
        print(response)
        print("*" * 30)
        if response:
            save_record(filename, response)
            os.remove(path + filename)
            print("Matched and record saved")
            return "2"
        else:
            #No match was found
            if "_attempt1" in filename:
                response  = {'offset': 0, 'confidence': 0, 'offset_seconds': 0, 'match_time': 0, 'song_name': 'None', 'dejavu_log':''}
                save_record(filename, response)
                os.remove(path + filename)
                print("Did not match and record saved")
                return "0"
            else:
                new_filename = filename.split('.')[0] + "_attempt1.wav"
                os.rename(path + filename, path + new_filename)
                print("Did not match, will try again")
                return "1"


if __name__ == '__main__':
     run()