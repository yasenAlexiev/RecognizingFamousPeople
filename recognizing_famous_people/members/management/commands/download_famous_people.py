import os
import re
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.conf import settings
from members.models import FamousPerson
import time
import random
import json

class Command(BaseCommand):
    help = 'Downloads images of famous people from Wikipedia and adds them to the database'

    def handle(self, *args, **options):
        media_path = os.path.join(settings.BASE_DIR, 'media')
        
        # Create media directory if it doesn't exist
        if not os.path.exists(media_path):
            os.makedirs(media_path)
            self.stdout.write(self.style.WARNING(f'Created media directory at {media_path}'))

        # Dictionary of famous people with their attributes
        # Format: 'Name': (gender, skin_color, difficulty)
        famous_people = {
            # Very famous scientists and inventors (easy)
            "Albert Einstein": ("male", "white", "easy"),
            "Stephen Hawking": ("male", "white", "easy"),
            "Elon Musk": ("male", "white", "easy"),
            "Bill Gates": ("male", "white", "easy"),
            "Steve Jobs": ("male", "white", "easy"),
            "Nikola Tesla": ("male", "white", "easy"),
            "Thomas Edison": ("male", "white", "easy"),
            "Isaac Newton": ("male", "white", "easy"),
            "Marie Curie": ("female", "white", "easy"),
            
            # Famous artists (easy)
            "Leonardo da Vinci": ("male", "white", "easy"),
            "Pablo Picasso": ("male", "white", "easy"),
            "Vincent van Gogh": ("male", "white", "easy"),
            "William Shakespeare": ("male", "white", "easy"),
            
            # Famous musicians (easy)
            "Michael Jackson": ("male", "black", "easy"),
            "Elvis Presley": ("male", "white", "easy"),
            "John Lennon": ("male", "white", "easy"),
            "Freddie Mercury": ("male", "white", "easy"),
            "David Bowie": ("male", "white", "easy"),
            
            # Very famous actors (easy)
            "Tom Hanks": ("male", "white", "easy"),
            "Leonardo DiCaprio": ("male", "white", "easy"),
            "Brad Pitt": ("male", "white", "easy"),
            "Jennifer Lawrence": ("female", "white", "easy"),
            "Meryl Streep": ("female", "white", "easy"),
            "Denzel Washington": ("male", "black", "easy"),
            "Scarlett Johansson": ("female", "white", "easy"),
            "Robert Downey Jr.": ("male", "white", "easy"),
            
            # Modern tech leaders (easy)
            "Mark Zuckerberg": ("male", "white", "easy"),
            "Jeff Bezos": ("male", "white", "easy"),
            "Sundar Pichai": ("male", "brown", "easy"),
            "Tim Cook": ("male", "white", "easy"),
            
            # Current political leaders (easy)
            "Joe Biden": ("male", "white", "easy"),
            "Barack Obama": ("male", "black", "easy"),
            "Donald Trump": ("male", "white", "easy"),
            
            # Less known but notable figures (hard)
            "Jensen Huang": ("male", "brown", "hard"),
            "Satya Nadella": ("male", "brown", "hard"),
            "Reed Hastings": ("male", "white", "hard"),
            "Brian Chesky": ("male", "white", "hard"),
            "Jack Dorsey": ("male", "white", "hard"),
            "Susan Wojcicki": ("female", "white", "hard"),
            "Shantanu Narayen": ("male", "brown", "hard"),
            
            # Less known actors (hard)
            "Florence Pugh": ("female", "white", "hard"),
            "Anya Taylor-Joy": ("female", "white", "hard"),
            "Austin Butler": ("male", "white", "hard"),
            "Sydney Sweeney": ("female", "white", "hard"),
            "Timothée Chalamet": ("male", "white", "hard"),
            
            # Less known musicians (hard)
            "Post Malone": ("male", "white", "hard"),
            "Kendrick Lamar": ("male", "black", "hard"),
            "The Weeknd": ("male", "black", "hard"),
            "Dua Lipa": ("female", "white", "hard"),
            
            # Less known political figures (hard)
            "Emmanuel Macron": ("male", "white", "hard"),
            "Justin Trudeau": ("male", "white", "hard"),
            "Volodymyr Zelenskyy": ("male", "white", "hard"),
            "Narendra Modi": ("male", "brown", "hard"),
            "Rishi Sunak": ("male", "brown", "hard")
        }

        people_to_download = list(famous_people.items())

        for person, attributes in people_to_download:
            try:
                gender, skin_color, difficulty = attributes
                
                # Format the name for the filename - remove all special characters
                filename = re.sub(r'[^a-zA-Z0-9]', '', person) + '.jpg'
                filepath = os.path.join(media_path, filename)

                # Skip if person already exists in database
                if FamousPerson.objects.filter(name=person).exists():
                    self.stdout.write(self.style.WARNING(f'{person} already exists in database, skipping...'))
                    continue

                # Skip if file already exists
                if os.path.exists(filepath):
                    self.stdout.write(self.style.WARNING(f'Image for {person} already exists, skipping...'))
                    continue

                # Get Wikipedia page
                wiki_url = f"https://en.wikipedia.org/wiki/{person.replace(' ', '_')}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                }
                
                response = requests.get(wiki_url, headers=headers)
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f'Failed to access Wikipedia page for {person}'))
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the infobox image
                infobox = soup.find('table', {'class': 'infobox'})
                if not infobox:
                    self.stdout.write(self.style.ERROR(f'No infobox found for {person}'))
                    continue

                # Find the first image in the infobox
                img = infobox.find('img')
                if not img:
                    self.stdout.write(self.style.ERROR(f'No image found in infobox for {person}'))
                    continue

                # Get the image URL
                img_url = img.get('src')
                if not img_url:
                    self.stdout.write(self.style.ERROR(f'No image URL found for {person}'))
                    continue

                # Convert relative URL to absolute
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://en.wikipedia.org' + img_url

                # Download the image
                img_response = requests.get(img_url, headers=headers)
                if img_response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    # Create database entry with attributes from the dictionary
                    FamousPerson.objects.create(
                        name=person,
                        image=filename,
                        difficulty=difficulty,
                        gender=gender,
                        skin_color=skin_color
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'Successfully downloaded and added {person}'))
                    
                    # Add a small delay to avoid overwhelming the server
                    time.sleep(random.uniform(1, 3))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to download image for {person}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {person}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Finished downloading famous people'))
