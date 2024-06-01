from django.urls import path
from . import views

urlpatterns = [
    path('submit_assignment/<int:id>', views.SubmitAssignment.as_view(), name='submit_assignment'),
    path('get_all_assignments/', views.GetAllAssignments.as_view(), name='get_assignments'),
    path('get_assignments/<str:id>/', views.GetAssignments.as_view(), name='get_assignments'),
    path('get_assignment/<int:id>/', views.GetAssignment.as_view(), name='get_assignment'), 
    path('submit_answer/<int:id>', views.AnswerView.as_view(), name='answer'),
    path('get_result/<int:id>/', views.ResultView.as_view(), name='result'),
    path('upload_question/', views.UploadQuestion.as_view(), name='upload_question'),
    path('get_courses/', views.GetStudentCourses.as_view(), name='get_courses')
]

