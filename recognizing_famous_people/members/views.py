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
from django.views.decorators.csrf import csrf_exempt

def get_random_images(count=90):
    """Get random images from the database for the login page background."""
    all_people = list(FamousPerson.objects.all())
    if len(all_people) < count:
        return all_people
    return random.sample(all_people, count)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('difficulty')
        else:
            error_message = "Invalid username or password"
    else:
        error_message = None
    
    # Get random images for the background
    random_people = get_random_images()
    print(random_people[0].image.url)
    
    return render(request, 'login.html', {
        'error_message': error_message,
        'random_people': random_people
    })

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            return render(request, 'signup.html', {
                'error_message': 'Passwords do not match.',
                'random_people': get_random_images()
            })
        
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'signup.html', {
                'error_message': 'Username already exists.',
                'random_people': get_random_images()
            })
        
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'signup.html', {
                'error_message': 'Email already registered.',
                'random_people': get_random_images()
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
    
    return render(request, 'signup.html', {
        'random_people': get_random_images()
    })

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
    # Get random people for the conveyor belt
    random_people = get_random_images(40)  # Get 40 images for the conveyor belt
    
    return render(request, 'difficulty.html', {
        'user': user,
        'random_people': random_people
    })

@method_decorator(login_required, name='dispatch')
class QuizView(View):
    def get(self, request, difficulty):
        # Get the current session score
        session_score = request.session.get('session_score', 0)
        
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
        
        # Store the current question data in the session
        current_question = {
            'image1_url': selected_people[0].image.url,
            'image2_url': selected_people[1].image.url,
            'correct_person_name': correct_person.name,
            'correct_image_index': correct_index,
            'person1_id': selected_people[0].id,
            'person2_id': selected_people[1].id
        }
        request.session['current_question'] = current_question
        
        # Get user's current score and best scores
        user = CustomUser.objects.get(id=request.user.id)
        
        context = {
            'image1_url': current_question['image1_url'],
            'image2_url': current_question['image2_url'],
            'correct_person_name': current_question['correct_person_name'],
            'correct_image_index': current_question['correct_image_index'],
            'difficulty': difficulty,
            'current_score': user.score,
            'session_score': session_score,
            'best_score_easy': user.best_score_easy,
            'best_score_medium': user.best_score_medium,
            'best_score_hard': user.best_score_hard
        }
        
        return render(request, 'quiz_page.html', context)
    
    def post(self, request, difficulty):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        try:
            data = json.loads(request.body)
            selected_index = data.get('selected_index')
            correct_index = data.get('correct_index')
            
            # Get current session score
            session_score = request.session.get('session_score', 0)
            user = CustomUser.objects.get(id=request.user.id)
            
            # Only increment scores if the answer is correct
            if selected_index == correct_index:
                user.score += 1
                user.save()
                
                # Increment the session score only for correct answers
                session_score += 1
                request.session['session_score'] = session_score
                
                # Update best score if current session score is higher
                best_score_field = f'best_score_{difficulty}'
                current_best = getattr(user, best_score_field)
                if session_score > current_best:
                    setattr(user, best_score_field, session_score)
                    user.save()
                
                return JsonResponse({
                    'new_score': user.score,
                    'new_session_score': session_score,
                    'new_best_score': getattr(user, best_score_field),
                    'game_over': False
                })
            else:
                # Game over - wrong answer
                return JsonResponse({
                    'new_score': user.score,
                    'new_session_score': session_score,
                    'game_over': True
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

