from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import FamousPerson, CustomUser
import random


def members(request):
    template = loader.get_template("home_page.html")
    return HttpResponse(template.render({}, request))

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {
                'error_message': 'Invalid username or password.'
            })
    
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            return render(request, 'signup.html', {
                'error_message': 'Passwords do not match.'
            })
        
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'signup.html', {
                'error_message': 'Username already exists.'
            })
        
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'signup.html', {
                'error_message': 'Email already registered.'
            })
        
        # Create the user
        user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                score=0
            )
        
        # Log the user in
        login(request, user)
        return redirect('home')
    
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@method_decorator(login_required, name='dispatch')
class QuizView(View):
    def get(self, request, difficulty):
        # Get two random famous people of the specified difficulty
        famous_people = list(FamousPerson.objects.filter(difficulty=difficulty))
        
        if len(famous_people) < 2:
            return render(request, 'error.html', {
                'message': 'Not enough famous people in the database for this difficulty level.'
            })
        
        # Randomly select two different people
        selected_people = random.sample(famous_people, 2)
        
        # Randomly choose which one will be the correct answer
        correct_index = random.randint(0, 1)
        correct_person = selected_people[correct_index]
        
        # Get user's current score
        user = CustomUser.objects.get(id=request.user.id)
        
        context = {
            'image1_url': selected_people[0].image.url,
            'image2_url': selected_people[1].image.url,
            'correct_person_name': correct_person.name,
            'correct_image_index': correct_index,
            'difficulty': difficulty,
            'current_score': user.score
        }
        
        return render(request, 'quiz_page.html', context)
    
    def post(self, request, difficulty):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
            
        user = CustomUser.objects.get(id=request.user.id)
        user.score += 1
        user.save()
        
        return JsonResponse({'new_score': user.score})

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home_page.html')

