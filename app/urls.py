from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'login/', auth_views.login, name='login'),
    path(r'logout/', auth_views.logout, name='logout'),
    path('', views.index, name='index'),
    path('instructor-input', views.instructor_input),
    path('student-input', views.student_input),
    path('mark-as-present', views.mark_as_present),
    path('mark-as-absent', views.mark_as_absent),
    path('ieor171', views.student),
    path('report', views.instructor_report),
    path('history', views.student_history),
    path('poll', views.polling_results),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
