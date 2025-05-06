from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/<str:difficulty>/', views.QuizView.as_view(), name='quiz'),
]

