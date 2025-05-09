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
import json

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('difficulty')
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
        return redirect('difficulty')
    
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def difficulty(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Reset all quiz-related session variables when returning to difficulty page
    request.session['guess_count'] = 0
    request.session['session_score'] = 0
    
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, 'difficulty.html', {'user': user})

@method_decorator(login_required, name='dispatch')
class QuizView(View):
    def get(self, request, difficulty):
        # Get the current guess count
        guess_count = request.session.get('guess_count', 0)
        
        # If we've reached 10 guesses, redirect to results page
        if guess_count >= 10:
            # Get the final session score
            request.session['session_score'] = session_score
            return redirect('quiz_results')
            
        # Get famous people of the specified difficulty
        famous_people = FamousPerson.objects.filter(difficulty=difficulty)
        
        if famous_people.count() < 2:
            return render(request, 'error.html', {
                'message': 'Not enough famous people in the database for this difficulty level.'
            })
        
        # Select first person randomly
        selected_first_person = random.sample(list(famous_people), 1)[0]
        
        # Select second person based on difficulty
        if difficulty == 'easy':
            second_person_queryset = famous_people.filter(gender=selected_first_person.gender).exclude(id=selected_first_person.id)
        elif difficulty == 'medium':
            second_person_queryset = famous_people.filter(
                gender=selected_first_person.gender,
                skin_color=selected_first_person.skin_color
            ).exclude(id=selected_first_person.id)
        elif difficulty == 'hard':
            second_person_queryset = famous_people.filter(
                gender=selected_first_person.gender,
                skin_color=selected_first_person.skin_color
            ).exclude(id=selected_first_person.id)
        
        if second_person_queryset.count() == 0:
            return render(request, 'error.html', {
                'message': 'Not enough similar famous people in the database for this difficulty level.'
            })
            
        selected_second_person = random.sample(list(second_person_queryset), 1)[0]
        selected_people = [selected_first_person, selected_second_person]
        
        # Randomly choose which one will be the correct answer
        correct_index = random.randint(0, 1)
        correct_person = selected_people[correct_index]
        
        # Get user's current score and session score
        user = CustomUser.objects.get(id=request.user.id)
        session_score = request.session.get('session_score', 0)
        
        # Increment guess count for every question
        request.session['guess_count'] = guess_count + 1
        
        context = {
            'image1_url': selected_people[0].image.url,
            'image2_url': selected_people[1].image.url,
            'correct_person_name': correct_person.name,
            'correct_image_index': correct_index,
            'difficulty': difficulty,
            'current_score': user.score,
            'session_score': session_score,
            'guess_count': guess_count + 1,
            'total_guesses': 10
        }
        
        return render(request, 'quiz_page.html', context)
    
    def post(self, request, difficulty):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        try:
            data = json.loads(request.body)
            selected_index = data.get('selected_index')
            correct_index = data.get('correct_index')
            
            # Only increment scores if the answer is correct
            if selected_index == correct_index:
                user = CustomUser.objects.get(id=request.user.id)
                user.score += 1
                user.save()
                
                # Increment the session score only for correct answers
                session_score = request.session.get('session_score', 0) + 1
                request.session['session_score'] = session_score
                
                return JsonResponse({
                    'new_score': user.score,
                    'new_session_score': session_score
                })
            else:
                # Return current scores without incrementing
                user = CustomUser.objects.get(id=request.user.id)
                session_score = request.session.get('session_score', 0)
                return JsonResponse({
                    'new_score': user.score,
                    'new_session_score': session_score
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def quiz_results(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    session_score = request.session.get('session_score', 0)
    print(session_score)
    
    # Generate appropriate message based on score
    if session_score >= 8:
        message = "Outstanding! You're a true celebrity expert! 🏆"
    elif session_score >= 5:
        message = "Great job! You know your celebrities well! ⭐"
    else:
        message = "Keep practicing! You'll get better with time! 💪"
    
    # Reset session variables after showing results
    request.session['guess_count'] = 0
    request.session['session_score'] = 0
    
    return render(request, 'quiz_results.html', {
        'session_score': session_score,
        'message': message
    })

