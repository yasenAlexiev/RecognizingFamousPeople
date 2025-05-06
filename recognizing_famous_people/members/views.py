from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views import View
from .models import FamousPerson
import random


def members(request):
    template = loader.get_template("home_page.html")
    return HttpResponse(template.render({}, request))

def easy_quiz(request):
    template = loader.get_template("easy_quiz.html")
    return HttpResponse(template.render({}, request))

def medium_quiz(request):
    template = loader.get_template("medium_quiz.html")
    return HttpResponse(template.render({}, request))

def hard_quiz(request):
    template = loader.get_template("hard_quiz.html")
    return HttpResponse(template.render({}, request))

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
        
        context = {
            'image1_url': selected_people[0].image.url,
            'image2_url': selected_people[1].image.url,
            'correct_person_name': correct_person.name,
            'correct_image_index': correct_index,
            'difficulty': difficulty
        }
        
        return render(request, 'quiz_page.html', context)

def home(request):
    return render(request, 'home_page.html')

