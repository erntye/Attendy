# chat/consumers.py
from channels.generic.websocket import WebsocketConsumer
import json
from dejavu import Dejavu
from app.models import *
from datetime import datetime

with open("dejavu.cnf.SAMPLE") as f:
    config = json.load(f)

class AudioConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, data):
        text_data_json = json.loads(data)
        session = text_data_json['SESSIONNAME']
        class_id = text_data_json['CLASSID']
        version = text_data_json['VERSIONNAME']
        user_id = text_data_json['USERID']
        audio = text_data_json['audio']
        djv = Dejavu(config)

        filename = 'media/instructor/instructor_' + user_id +'_' + class_id + '_' + session +'_' + version +'.wav'
        uploadedFile = open(filename, "wb")
        uploadedFile.write(audio)
        uploadedFile.close()

        c = Classroom.objects.get(id=1)  # hardcoded
        u = User.objects.get(id=1)
        InstructorInbound(user = u, classroom = c, session = session, time_in=datetime.now()).save()

        djv.fingerprint_directory("media/instructor/", [".wav"])
        response = djv.db.get_num_fingerprints()
        self.send(text_data=json.dumps({
            'message': "received",
            'fingerprints': response
        }))