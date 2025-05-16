# Famous People Recognition Game

A Django-based web application that tests your knowledge of famous people through an engaging quiz game. Players are presented with pairs of images and must identify the correct person based on the given name.

## Features

- **Multiple Difficulty Levels**
  - Easy: Clear, recent photos
  - Medium: Mix of recent and historical photos
  - Hard: Challenging historical photos

- **Score Tracking**
  - Session scores for current gameplay
  - Best scores for each difficulty level
  - Persistent score tracking for registered users

- **Endless Mode**
  - Play until you make a mistake
  - Challenge yourself to beat your high score
  - Immediate feedback on your choices

- **User-Friendly Interface**
  - Clean, modern design
  - Responsive layout
  - Intuitive image selection
  - Visual feedback for correct/incorrect answers

## Technologies Used

- **Backend**
  - Django 4.2+
  - Python 3.8+
  - SQLite/PostgreSQL database

- **Frontend**
  - HTML5
  - CSS3
  - JavaScript
  - Responsive design

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/RecognizingFamousPeople.git
   cd RecognizingFamousPeople
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   cd recognizing_famous_people
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

6. Visit `http://127.0.0.1:8000` in your browser

## Game Rules

1. Choose a difficulty level (Easy, Medium, or Hard)
2. You'll be shown two images and a famous person's name
3. Click on the image that matches the given name
4. Correct answers increase your score
5. The game continues until you make a mistake
6. Try to beat your best score for each difficulty level!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Testing

Run the test suite:
```bash
python manage.py test
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped improve the game
- Special thanks to the Django community for their excellent documentation
- Image credits to respective photographers and sources

## Contact

For any questions or suggestions, please open an issue in the GitHub repository.