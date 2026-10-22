
import random
import urllib.request

# Download the word list
url = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt"


# ASCII gallows stages
HANGMAN_STAGES = [
    """
     +---+
     |   |
         |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
     |   |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|   |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
    =========
    """
]


# Load words from the online word list
def load_words():
    try:
        response = urllib.request.urlopen(url, timeout=10)

        with response:
            text = response.read().decode("utf-8")

        words = [
            word.strip().lower()
            for word in text.splitlines()
            if word.strip().isalpha()
            and 4 <= len(word.strip()) <= 12
        ]

        if words:
            return words

        print("The downloaded word list is empty.")

    except Exception:
        print("Unable to download the word list.")

    # Backup words if the internet is unavailable
    return ["python", "computer", "program", "database", "network"]


# Display the current hangman stage
def display_hangman(wrong_count):
    print(HANGMAN_STAGES[wrong_count])


# Display the hidden word
def display_word(word, guessed_letters):
    display = ""

    for letter in word:
        if letter in guessed_letters:
            display += letter + " "
        else:
            display += "_ "

    return display.strip()


# Play one round of Hangman
def play_game(words):
    word = random.choice(words)

    guessed_letters = set()
    wrong_letters = set()
    attempts = 6

    print("\n===== HANGMAN GAME =====")
    print("Guess the hidden word one letter at a time.")
    print("You have 6 incorrect guesses allowed.")

    while attempts > 0:

        # Display the current game status
        display_hangman(6 - attempts)

        print("\nWord:", display_word(word, guessed_letters))
        print("Correct guesses:", sorted(guessed_letters))
        print("Wrong guesses:", sorted(wrong_letters))
        print("Attempts remaining:", attempts)

        # Check whether the player has won
        if all(letter in guessed_letters for letter in word):
            print("\nCongratulations! You guessed the word!")
            print("The word was:", word)
            print("===== YOU WIN! =====")
            return

        # Get a letter from the player
        guess = input("\nEnter a letter: ").strip().lower()

        # Validate the input
        if len(guess) != 1 or not guess.isalpha():
            print("Invalid input! Please enter one letter.")
            continue

        # Prevent duplicate guesses
        if guess in guessed_letters or guess in wrong_letters:
            print("You already guessed that letter!")
            continue

        # Check the guessed letter
        if guess in word:
            guessed_letters.add(guess)
            print("Correct guess!")
        else:
            wrong_letters.add(guess)
            attempts -= 1
            print("Wrong guess!")

    # Display the final stage
    display_hangman(6)

    print("\n===== GAME OVER =====")
    print("You have used all 6 incorrect guesses.")
    print("The correct word was:", word)


# Main function
def main():
    words = load_words()

    print("Words loaded:", len(words))

    while True:
        play_game(words)

        again = input("\nWould you like to play again? (yes/no): ")
        if again.strip().lower() not in ("yes", "y"):
            print("\nThanks for playing Hangman!")
            break


# Start the game
if __name__ == "__main__":
    main()
