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

        # Initialize counter for successfully downloaded people
        successful_downloads = 0
        
        # Dictionary of famous people with their attributes
        # Format: 'Name': (gender, skin_color, difficulty)
        famous_people = {
            # Very famous scientists and inventors (easy)
            "Albert Einstein":    ("male",   "white", "easy"),
            "Stephen Hawking":    ("male",   "white", "easy"),
            "Elon Musk":         ("male",   "white", "easy"),
            "Bill Gates":        ("male",   "white", "easy"),
            "Steve Jobs":        ("male",   "white", "easy"),
            "Nikola Tesla":      ("male",   "white", "easy"),
            "Thomas Edison":     ("male",   "white", "easy"),
            "Isaac Newton":      ("male",   "white", "easy"),
            "Marie Curie":       ("female", "white", "easy"),
            
            # Famous artists (easy)
            "Leonardo da Vinci": ("male",   "white", "easy"),
            "Pablo Picasso":     ("male",   "white", "easy"),
            "Vincent van Gogh":  ("male",   "white", "easy"),
            "William Shakespeare":("male",   "white", "easy"),
            
            # Very famous actors (easy)
            "Tom Hanks":         ("male",   "white", "easy"),
            "Leonardo DiCaprio": ("male",   "white", "easy"),
            "Brad Pitt":         ("male",   "white", "easy"),
            "Jennifer Lawrence": ("female", "white", "easy"),
            "Meryl Streep":      ("female", "white", "easy"),
            "Denzel Washington": ("male",   "black", "easy"),
            "Scarlett Johansson":("female", "white", "easy"),
            "Robert Downey Jr.": ("male",   "white", "easy"),
            "Will Smith":        ("male",   "black", "easy"),
            "Tom Cruise":        ("male",   "white", "easy"),
            "Morgan Freeman":    ("male",   "black", "easy"),
            "Samuel L. Jackson": ("male",   "black", "easy"),
            "Emma Watson":       ("female", "white", "easy"),
            "Jennifer Aniston":  ("female", "white", "easy"),
            "George Clooney":    ("male",   "white", "easy"),
            "Julia Roberts":     ("female", "white", "easy"),
            "Johnny Depp":       ("male",   "white", "easy"),
            "Angelina Jolie":    ("female", "white", "easy"),
            "Chris Hemsworth":   ("male",   "white", "easy"),
            "Chris Evans":       ("male",   "white", "easy"),
            "Mark Ruffalo":      ("male",   "white", "easy"),
            "Chris Pratt":       ("male",   "white", "easy"),
            "Gal Gadot":         ("female", "white", "easy"),
            "Dwayne Johnson":    ("male",   "brown", "easy"),
            "Ryan Reynolds":     ("male",   "white", "easy"),
            "Hugh Jackman":      ("male",   "white", "easy"),
            "Anne Hathaway":     ("female", "white", "easy"),
            "Emma Stone":        ("female", "white", "easy"),
            "Ryan Gosling":      ("male",   "white", "easy"),
            "Margot Robbie":     ("female", "white", "easy"),
            
            # Famous musicians (easy)
            "Michael Jackson":   ("male",   "black", "easy"),
            "Elvis Presley":     ("male",   "white", "easy"),
            "John Lennon":       ("male",   "white", "easy"),
            "Freddie Mercury":   ("male",   "white", "easy"),
            "David Bowie":       ("male",   "white", "easy"),
            "Madonna":          ("female", "white", "easy"),
            "Beyoncé":          ("female", "black", "easy"),
            "Taylor Swift":      ("female", "white", "easy"),
            "Lady Gaga":         ("female", "white", "easy"),
            "Rihanna":          ("female", "black", "easy"),
            "Justin Bieber":     ("male",   "white", "easy"),
            "Ed Sheeran":       ("male",   "white", "easy"),
            "Adele":            ("female", "white", "easy"),
            "Bruno Mars":        ("male",   "brown", "easy"),
            "Drake":            ("male",   "black", "easy"),
            "Eminem":           ("male",   "white", "easy"),
            "Kanye West":        ("male",   "black", "easy"),
            "Jay-Z":            ("male",   "black", "easy"),
            "Katy Perry":        ("female", "white", "easy"),
            "Ariana Grande":     ("female", "white", "easy"),
            
            # Famous authors (easy)
            "J.K. Rowling":      ("female", "white", "easy"),
            "Stephen King":      ("male",   "white", "easy"),
            "George R.R. Martin":("male",   "white", "easy"),
            "Dan Brown":         ("male",   "white", "easy"),
            "John Grisham":      ("male",   "white", "easy"),
            "Agatha Christie":   ("female", "white", "easy"),
            "Ernest Hemingway":  ("male",   "white", "easy"),
            "Mark Twain":        ("male",   "white", "easy"),
            "Charles Dickens":   ("male",   "white", "easy"),
            "Jane Austen":       ("female", "white", "easy"),
            
            # Famous directors (easy)
            "Steven Spielberg":  ("male",   "white", "easy"),
            "James Cameron":     ("male",   "white", "easy"),
            "Christopher Nolan": ("male",   "white", "easy"),
            "Martin Scorsese":   ("male",   "white", "easy"),
            "Quentin Tarantino":("male",   "white", "easy"),
            "George Lucas":      ("male",   "white", "easy"),
            "Peter Jackson":     ("male",   "white", "easy"),
            "Ridley Scott":      ("male",   "white", "easy"),
            "Tim Burton":        ("male",   "white", "easy"),
            "Alfred Hitchcock":  ("male",   "white", "easy"),
            
            # Modern tech leaders (easy)
            "Mark Zuckerberg":   ("male",   "white", "easy"),
            "Jeff Bezos":        ("male",   "white", "easy"),
            "Sundar Pichai":     ("male",   "asian", "easy"),
            "Tim Cook":          ("male",   "white", "easy"),
            
            # Current political leaders (easy)
            "Joe Biden":         ("male",   "white", "easy"),
            "Barack Obama":      ("male",   "black", "easy"),
            "Donald Trump":      ("male",   "white", "easy"),
            
            # Medium difficulty actors
            "Florence Pugh":     ("female", "white", "medium"),
            "Anya Taylor-Joy":   ("female", "white", "medium"),
            "Austin Butler":     ("male",   "white", "medium"),
            "Sydney Sweeney":    ("female", "white", "medium"),
            "Timothée Chalamet":("male",   "white", "medium"),
            "Zendaya":          ("female", "black", "medium"),
            "Jacob Elordi":      ("male",   "white", "medium"),
            "Millie Bobby Brown":("female", "white", "medium"),
            "Tom Holland":       ("male",   "white", "medium"),
            "Hailee Steinfeld":  ("female", "white", "medium"),
            "Ansel Elgort":      ("male",   "white", "medium"),
            "Lily Collins":      ("female", "white", "medium"),
            "Noah Centineo":     ("male",   "white", "medium"),
            "Lana Condor":       ("female", "asian", "medium"),
            "Henry Golding":     ("male",   "asian", "medium"),
            "Awkwafina":         ("female", "asian", "medium"),
            "Simu Liu":          ("male",   "asian", "medium"),
            "Gemma Chan":        ("female", "asian", "medium"),
            "John Boyega":       ("male",   "black", "medium"),
            "Letitia Wright":    ("female", "black", "medium"),
            
            # Medium difficulty musicians
            "Post Malone":       ("male",   "white", "medium"),
            "Kendrick Lamar":    ("male",   "black", "medium"),
            "The Weeknd":        ("male",   "black", "medium"),
            "Dua Lipa":          ("female", "white", "medium"),
            "Billie Eilish":     ("female", "white", "medium"),
            "Lil Nas X":         ("male",   "black", "medium"),
            "Doja Cat":          ("female", "black", "medium"),
            "Megan Thee Stallion":("female", "black", "medium"),
            "Cardi B":           ("female", "black", "medium"),
            "Bad Bunny":         ("male",   "brown", "medium"),
            "J Balvin":          ("male",   "brown", "medium"),
            "Rosalía":           ("female", "white", "medium"),
            "BTS":               ("male",   "asian", "medium"),
            "BLACKPINK":         ("female", "asian", "medium"),
            "Harry Styles":      ("male",   "white", "medium"),
            "Lizzo":             ("female", "black", "medium"),
            "Halsey":            ("female", "white", "medium"),
            "Shawn Mendes":      ("male",   "white", "medium"),
            "Camila Cabello":    ("female", "brown", "medium"),
            "The Kid LAROI":     ("male",   "brown", "medium"),
            
            # Medium difficulty authors
            "Colleen Hoover":    ("female", "white", "medium"),
            "Sally Rooney":      ("female", "white", "medium"),
            "Taylor Jenkins Reid":("female", "white", "medium"),
            "Emily Henry":       ("female", "white", "medium"),
            "Ali Hazelwood":     ("female", "white", "medium"),
            "Rebecca Yarros":    ("female", "white", "medium"),
            "Madeline Miller":   ("female", "white", "medium"),
            "V.E. Schwab":       ("female", "white", "medium"),
            "Leigh Bardugo":     ("female", "white", "medium"),
            "Sarah J. Maas":     ("female", "white", "medium"),
            
            # Medium difficulty directors
            "Greta Gerwig":      ("female", "white", "medium"),
            "Jordan Peele":      ("male",   "black", "medium"),
            "Taika Waititi":     ("male",   "brown", "medium"),
            "Denis Villeneuve":  ("male",   "white", "medium"),
            "Damien Chazelle":   ("male",   "white", "medium"),
            "Ari Aster":         ("male",   "white", "medium"),
            "Robert Eggers":     ("male",   "white", "medium"),
            "Barry Jenkins":     ("male",   "black", "medium"),
            "Ryan Coogler":      ("male",   "black", "medium"),
            "Chloé Zhao":        ("female", "asian", "medium"),
            
            # Less known but notable figures (hard)
            "Jensen Huang":      ("male",   "asian", "hard"),
            "Satya Nadella":     ("male",   "asian", "hard"),
            "Reed Hastings":     ("male",   "white", "hard"),
            "Brian Chesky":      ("male",   "white", "hard"),
            "Jack Dorsey":       ("male",   "white", "hard"),
            "Susan Wojcicki":    ("female", "white", "hard"),
            "Shantanu Narayen":  ("male",   "asian", "hard"),
            
            # Hard difficulty actors
            "Jenna Ortega":      ("female", "brown", "hard"),
            "Jacob Tremblay":    ("male",   "white", "hard"),
            "Mckenna Grace":     ("female", "white", "hard"),
            "Iman Vellani":      ("female", "asian", "hard"),
            "Dominic Sessa":     ("male",   "white", "hard"),
            "Rachel Zegler":     ("female", "brown", "hard"),
            "Xolo Maridueña":    ("male",   "brown", "hard"),
            "Isabela Merced":    ("female", "brown", "hard"),
            "Mason Gooding":     ("male",   "black", "hard"),
            "Storm Reid":        ("female", "black", "hard"),
            
            # Hard difficulty musicians
            "Ice Spice":         ("female", "black", "hard"),
            "PinkPantheress":    ("female", "asian", "hard"),
            "Steve Lacy":        ("male",   "black", "hard"),
            "Omar Apollo":       ("male",   "brown", "hard"),
            "Rina Sawayama":     ("female", "asian", "hard"),
            "Beabadoobee":       ("female", "asian", "hard"),
            "Arlo Parks":        ("female", "black", "hard"),
            "Clairo":            ("female", "white", "hard"),
            "Remi Wolf":         ("female", "white", "hard"),
            "Wet Leg":           ("female", "white", "hard"),
            
            # Hard difficulty authors
            "R.F. Kuang":        ("female", "asian", "hard"),
            "Xiran Jay Zhao":    ("female", "asian", "hard"),
            "T.J. Klune":        ("male",   "white", "hard"),
            "Travis Baldree":    ("male",   "white", "hard"),
            "Shelley Parker-Chan":("female", "asian", "hard"),
            "Fonda Lee":         ("female", "asian", "hard"),
            "Rebecca Roanhorse": ("female", "brown", "hard"),
            "P. Djèlí Clark":    ("male",   "black", "hard"),
            "N.K. Jemisin":      ("female", "black", "hard"),
            "Tasha Suri":        ("female", "asian", "hard"),
            
            # Hard difficulty directors
            "Celine Song":       ("female", "asian", "hard"),
            "A.V. Rockwell":     ("female", "black", "hard"),
            "Elegance Bratton":  ("male",   "black", "hard"),
            "Charlotte Wells":   ("female", "white", "hard"),
            "Alice Diop":        ("female", "black", "hard"),
            "Laura Poitras":     ("female", "white", "hard"),
            "Sara Dosa":         ("female", "white", "hard"),
            "Elena López Riera": ("female", "white", "hard"),
            "Lila Avilés":       ("female", "brown", "hard"),
            "Carla Simón":       ("female", "white", "hard"),
            
            # Less known political figures (hard)
            "Emmanuel Macron":   ("male",   "white", "hard"),
            "Justin Trudeau":    ("male",   "white", "hard"),
            "Volodymyr Zelenskyy":("male",  "white", "hard"),
            "Narendra Modi":     ("male",   "asian", "hard"),
            "Rishi Sunak":       ("male",   "asian", "hard"),

            # Show hosts (easy)
            "Jimmy Fallon":      ("male",   "white", "easy"),
            "Stephen Colbert":   ("male",   "white", "easy"),
            "Ellen DeGeneres":   ("female", "white", "easy"),
            "Oprah Winfrey":     ("female", "black", "easy"),
            "Conan O'Brien":     ("male",   "white", "easy"),
            "David Letterman":   ("male",   "white", "easy"),
            "Jay Leno":          ("male",   "white", "easy"),
            "Jimmy Kimmel":      ("male",   "white", "easy"),
            "Trevor Noah":       ("male",   "black", "easy"),
            "Seth Meyers":       ("male",   "white", "easy"),

            # Show hosts (medium)
            "John Oliver":       ("male",   "white", "medium"),
            "Samantha Bee":      ("female", "white", "medium"),
            "James Corden":      ("male",   "white", "medium"),
            "Kelly Clarkson":    ("female", "white", "medium"),
            "Drew Barrymore":    ("female", "white", "medium"),
            "Graham Norton":     ("male",   "white", "medium"),
            "Jonathan Ross":     ("male",   "white", "medium"),
            "Alan Carr":         ("male",   "white", "medium"),
            "Ricky Gervais":     ("male",   "white", "medium"),
            "Terry Crews":       ("male",   "black", "medium"),

            # Show hosts (hard)
            "Michelle Wolf":     ("female", "white", "hard"),
            "Hasan Minhaj":      ("male",   "asian", "hard"),
            "Ronny Chieng":      ("male",   "asian", "hard"),
            "Aasif Mandvi":      ("male",   "asian", "hard"),
            "Lilly Singh":       ("female", "asian", "hard"),
            "Desus Nice":        ("male",   "black", "hard"),
            "Mero":             ("male",   "black", "hard"),
            "Amber Ruffin":      ("female", "black", "hard"),
            "Ziwe":             ("female", "black", "hard"),
            "Joel McHale":       ("male",   "white", "hard")
        }

        people_to_download = list(famous_people.items())
        total_people = len(people_to_download)
        self.stdout.write(self.style.SUCCESS(f'Starting download of {total_people} famous people...'))

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
                    
                    successful_downloads += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully downloaded and added {person} ({successful_downloads} of {total_people})'))
                    
                    # Add a small delay to avoid overwhelming the server
                    time.sleep(random.uniform(1, 3))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to download image for {person}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {person}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Finished downloading famous people. Total successfully downloaded: {successful_downloads} of {total_people}'))
