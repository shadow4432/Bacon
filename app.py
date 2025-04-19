import sqlite3
import random

# Database setup
def initialize_db():
    conn = sqlite3.connect('bacon_social_media.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL
    )''')

    # Create posts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        content TEXT,
        image TEXT,
        timestamp TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    # Create videos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        length INTEGER,
        uploaded BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    # Create followers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS followers (
        id INTEGER PRIMARY KEY,
        follower_id INTEGER,
        followed_id INTEGER,
        FOREIGN KEY (follower_id) REFERENCES users(id),
        FOREIGN KEY (followed_id) REFERENCES users(id)
    )''')

    conn.commit()
    conn.close()

# Models for Social Media Features

# User Model
class User:
    def __init__(self, username):
        self.username = username
        self.id = None

    def save_to_db(self):
        conn = sqlite3.connect('bacon_social_media.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', (self.username,))
            conn.commit()
            cursor.execute('SELECT id FROM users WHERE username = ?', (self.username,))
            self.id = cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error saving user: {e}")
        finally:
            conn.close()

    def create_post(self, content, image=None):
        conn = sqlite3.connect('bacon_social_media.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO posts (user_id, content, image, timestamp) VALUES (?, ?, ?, ?)',
                           (self.id, content, image, "2025-04-19"))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating post: {e}")
        finally:
            conn.close()

    def follow(self, other_user):
        conn = sqlite3.connect('bacon_social_media.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO followers (follower_id, followed_id) VALUES (?, ?)',
                           (self.id, other_user.id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error following user: {e}")
        finally:
            conn.close()

    def unfollow(self, other_user):
        conn = sqlite3.connect('bacon_social_media.db')
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM followers WHERE follower_id = ? AND followed_id = ?',
                           (self.id, other_user.id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error unfollowing user: {e}")
        finally:
            conn.close()

    def get_follower_count(self):
        conn = sqlite3.connect('bacon_social_media.db')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM followers WHERE followed_id = ?', (self.id,))
            count = cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error fetching followers: {e}")
            count = 0
        finally:
            conn.close()
        return count

    def get_following_count(self):
        conn = sqlite3.connect('bacon_social_media.db')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM followers WHERE follower_id = ?', (self.id,))
            count = cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error fetching following count: {e}")
            count = 0
        finally:
            conn.close()
        return count

# Video Model
class Video:
    def __init__(self, title, uploader, length):
        self.title = title
        self.uploader = uploader
        self.length = length
        self.uploaded = False

    def upload(self):
        conn = sqlite3.connect('bacon_social_media.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO videos (user_id, title, length, uploaded) VALUES (?, ?, ?, ?)',
                           (self.uploader.id, self.title, self.length, 1))
            conn.commit()
            self.uploaded = True
        except sqlite3.Error as e:
            print(f"Error uploading video: {e}")
        finally:
            conn.close()

class VideoPlatform:
    def add_video(self, video):
        video.upload()

# Mini Game Model
class MiniGame:
    def __init__(self, game_name):
        self.game_name = game_name
        self.is_playing = False

    def start_game(self):
        if not self.is_playing:
            print(f"Starting {self.game_name}!")
            self.is_playing = True
            self.play_game()
        else:
            print(f"{self.game_name} is already running.")

    def play_game(self):
        print("Playing...")
        result = random.choice(["win", "lose"])
        print(f"You {result} the game!")
        self.is_playing = False

# Initialize Database
initialize_db()

# Main Program
def main():
    print("Welcome to the Bacon Social Media Platform!")
    username = input("Enter your username: ")

    # Check if user already exists
    conn = sqlite3.connect('bacon_social_media.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()

    if user_data:
        current_user = User(username)
        current_user.id = user_data[0]
        print(f"Welcome back, {current_user.username}!")
    else:
        current_user = User(username)
        current_user.save_to_db()
        print(f"Welcome, {current_user.username}!")

    conn.close()

    # Basic interaction loop
    while True:
        print("\nOptions:")
        print("1. Create a post")
        print("2. Upload a video")
        print("3. Follow someone")
        print("4. Unfollow someone")
        print("5. View followers/following")
        print("6. Play a mini game")
        print("7. Exit")
        
        choice = input("What would you like to do? ")

        if choice == "1":
            content = input("Enter your post content: ")
            image = input("Enter image filename (optional): ")
            current_user.create_post(content, image if image else None)
        
        elif choice == "2":
            video_title = input("Enter video title: ")
            try:
                video_length = int(input("Enter video length (in minutes): "))
            except ValueError:
                print("Please enter a valid number for video length.")
                continue
            video = Video(video_title, current_user, video_length)
            platform = VideoPlatform()
            platform.add_video(video)
        
        elif choice == "3":
            follow_username = input("Enter the username of the person you want to follow: ")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (follow_username,))
            follow_user_data = cursor.fetchone()
            if follow_user_data:
                follow_user = User(follow_username)
                follow_user.id = follow_user_data[0]
                current_user.follow(follow_user)
            else:
                print(f"User {follow_username} not found.")
        
        elif choice == "4":
            unfollow_username = input("Enter the username of the person you want to unfollow: ")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (unfollow_username,))
            unfollow_user_data = cursor.fetchone()
            if unfollow_user_data:
                unfollow_user = User(unfollow_username)
                unfollow_user.id = unfollow_user_data[0]
                current_user.unfollow(unfollow_user)
            else:
                print(f"User {unfollow_username} not found.")
        
        elif choice == "5":
            print(f"Followers: {current_user.get_follower_count()}")
            print(f"Following: {current_user.get_following_count()}")
        
        elif choice == "6":
            game_name = input("Enter the game name (e.g., Minesweeper): ")
            game = MiniGame(game_name)
            game.start_game()

        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select again.")

if __name__ == "__main__":
    main()
