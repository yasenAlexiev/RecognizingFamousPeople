from django.urls import path
from . import views

urlpatterns = [
    path('', views.difficulty, name='difficulty'),
    path('quiz/<str:difficulty>/', views.QuizView.as_view(), name='quiz'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]

