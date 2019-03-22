from django.contrib import admin

from .models import *

class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'user')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('studentID','email')

class ClassListAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom')

class ClassTimeAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'day', 'year', 'semester', 'start_time', 'end_time')

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student','classroom', 'session', 'ip', 'confidence_score', 'match_time', 'song_name','offset', 'offset_seconds','status', 'time_in')

class StudentInboundAdmin(admin.ModelAdmin):
    list_display = ('studentID','classroom', 'session','time_in')

class InstructorInboundAdmin(admin.ModelAdmin):
    list_display = ('user_id','classroom', 'session','time_in')


admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(ClassTime, ClassTimeAdmin)
admin.site.register(ClassList, ClassListAdmin)
admin.site.register(StudentInbound, StudentInboundAdmin)
admin.site.register(InstructorInbound, InstructorInboundAdmin)