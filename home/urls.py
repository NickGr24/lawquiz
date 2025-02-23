from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('discipline/<int:discipline_id>/', views.quizzes_by_discipline, name='quizzes_by_discipline'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    path('add-question/', views.add_question, name='add_question'),
    path('get_quizzes/', views.get_quizzes, name='get_quizzes'),
]