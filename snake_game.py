#!/usr/bin/env python3
import curses
import random
import time
import sys
from datetime import datetime
from database_manager import SnakeGameDatabaseManager

# Initialize database manager
db = SnakeGameDatabaseManager()

# Global variables for player tracking
current_player = None
game_settings = {}
game_start_time = None

def safe_addch(stdscr, y, x, char, attr=curses.A_NORMAL):
    """Safely add a character to the screen, avoiding terminal boundary errors."""
    height, width = stdscr.getmaxyx()
    if 0 <= y < height - 1 and 0 <= x < width - 1:
        try:
            stdscr.addch(y, x, char, attr)
        except curses.error:
            pass

def safe_addstr(stdscr, y, x, string, attr=curses.A_NORMAL):
    """Safely add a string to the screen, avoiding terminal boundary errors."""
    height, width = stdscr.getmaxyx()
    if 0 <= y < height and 0 <= x < width:
        try:
            # Make sure the string doesn't extend beyond the screen width
            max_len = width - x - 1
            if len(string) > max_len:
                string = string[:max_len]
            stdscr.addstr(y, x, string, attr)
        except curses.error:
            pass

def check_terminal_size(stdscr):
    """Check if the terminal is large enough to play the game."""
    height, width = stdscr.getmaxyx()
    min_height, min_width = 20, 60
    
    if height < min_height or width < min_width:
        stdscr.clear()
        message = f"Terminal too small: {width}x{height}. Minimum required: {min_width}x{min_height}"
        try:
            stdscr.addstr(height // 2, max(0, (width - len(message)) // 2), message)
            stdscr.addstr(height // 2 + 1, max(0, (width - 21) // 2), "Press any key to exit.")
            stdscr.refresh()
            stdscr.getch()
        except curses.error:
            pass
        return False
    return True

def show_login_menu(stdscr):
    """Display login/registration menu and handle user selection."""
    # C    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Set input timeout for controlling game speed
    
    # Load game settings from database
    load_game_settings()
    
    # Show login menu and get player
    player = show_login_menu(stdscr)
    if player is None:
        return  # Exit if user cancels
    
    # Set current player
    current_player = player
    
    # Set up colors
    if not curses.has_colors():
        curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Food
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Score
    
    # Check if terminal is large enough
    if not check_terminal_size(stdscr):
        return
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Initial snake position and body
    snake_y = height // 2
    snake_x = width // 4
    snake = [(snake_y, snake_x), (snake_y, snake_x-1), (snake_y, snake_x-2)]
    
    # Initial food position - make sure it's not where the snake is
    food = create_food(height, width, snake)
    
    # Initial direction - moving right
    direction = curses.KEY_RIGHT
    
    # Initial score
    score = 0
    
    # Game state
    game_over = False
    
    # Record game start time
    game_start_time = datetime.now()

    # Draw border
    draw_border(stdscr)
    
    # Main game loop
    while not game_over:
        # Check if terminal was resized
        new_height, new_width = stdscr.getmaxyx()
        if new_height != height or new_width != width:
            # Terminal was resized, check if it's still large enough
            if not check_terminal_size(stdscr):
                return
            # Update dimensions
            height, width = new_height, new_width
            stdscr.clear()
            draw_border(stdscr)
        
        # Display score and player info
        player_info = f" Player: {current_player['username']} | Score: {score} "
        safe_addstr(stdscr, 0, 2, player_info, curses.color_pair(3))
        
        # Draw food
        safe_addch(stdscr, food[0], food[1], "●", curses.color_pair(2))
        
        # Get next key press but don't block
        key = stdscr.getch()
        
        # Handle key press for direction
        if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            # Prevent 180-degree turns
            if (key == curses.KEY_UP and direction != curses.KEY_DOWN) or \
               (key == curses.KEY_DOWN and direction != curses.KEY_UP) or \
               (key == curses.KEY_LEFT and direction != curses.KEY_RIGHT) or \
               (key == curses.KEY_RIGHT and direction != curses.KEY_LEFT):
                direction = key
        
        # Move snake in the current direction
        head_y, head_x = snake[0]
        if direction == curses.KEY_UP:
            head_y -= 1
        elif direction == curses.KEY_DOWN:
            head_y += 1
        elif direction == curses.KEY_LEFT:
            head_x -= 1
        elif direction == curses.KEY_RIGHT:
            head_x += 1
        
        # Add new head position
        snake.insert(0, (head_y, head_x))
        
        # Check if snake has eaten the food
        if snake[0] == food:
            score += game_settings["food_value"]
            food = create_food(height, width, snake)
            # Speed up slightly as score increases (but not too much)
            timeout = max(50, 100 - (score // 50) * 5)
            stdscr.timeout(timeout)
        else:
            # Remove tail if no food was eaten
            last = snake.pop()
            safe_addch(stdscr, last[0], last[1], " ")
        
        # Draw snake
        for i, (y, x) in enumerate(snake):
            char = "■" if i == 0 else "□"  # Different character for head
            safe_addch(stdscr, y, x, char, curses.color_pair(1))
        
        # Check for collisions with walls (excluding the score display area)
        if (head_y <= 0 or head_y >= height - 2 or head_x <= 0 or head_x >= width - 2):
            game_over = True
            
        # Check for collision with self
        if (head_y, head_x) in snake[1:]:
            game_over = True

        # Refresh the screen
        stdscr.refresh()
    
    # Game over screen
    show_game_over(stdscr, score)

def create_food(height, width, snake):
    """Create food at a random position that is not occupied by the snake."""
    while True:
        # Use safe boundaries for food (2 cells from borders)
        food = (random.randint(2, height - 3), random.randint(2, width - 3))
        if food not in snake:
            return food

def draw_border(stdscr):
    """Draw a border around the screen."""
    height, width = stdscr.getmaxyx()
    # Top and bottom borders (avoid the last column)
    for i in range(width - 1):
        safe_addch(stdscr, 0, i, "═")
        safe_addch(stdscr, height - 2, i, "═")
    
    # Left and right borders (avoid the last row)
    for i in range(height - 1):
        safe_addch(stdscr, i, 0, "║")
        safe_addch(stdscr, i, width - 2, "║")
    
    # Draw corners
    safe_addch(stdscr, 0, 0, "╔")
    safe_addch(stdscr, 0, width - 2, "╗")
    safe_addch(stdscr, height - 2, 0, "╚")
    safe_addch(stdscr, height - 2, width - 2, "╝")

def show_game_over(stdscr, score):
    """Display game over screen with final score."""
    global current_player, game_start_time
    
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # Calculate center position
    center_y = height // 2
    
    # Game over message
    game_over_msg = "GAME OVER!"
    safe_addstr(stdscr, center_y - 4, max(0, (width - len(game_over_msg)) // 2), 
               game_over_msg, curses.A_BOLD | curses.color_pair(2))
    
    # Score message
    score_msg = f"Final Score: {score}"
    safe_addstr(stdscr, center_y - 2, max(0, (width - len(score_msg)) // 2), 
               score_msg, curses.color_pair(3))
    
    # Save score to database if logged in
    if current_player and current_player['id'] is not None:
        # Calculate game duration
        game_end_time = datetime.now()
        duration = int((game_end_time - game_start_time).total_seconds())
        
        try:
            # Save game session
            db.connect()
            db.add_game_session(current_player['id'], score, duration)
            db.close()
            
            # Get player's highscore
            db.connect()
            highscore = db.get_player_highscore(current_player['id'])
            db.close()
            
            if highscore:
                highscore_msg = f"Your Highscore: {highscore['score']}"
                safe_addstr(stdscr, center_y, max(0, (width - len(highscore_msg)) // 2), 
                           highscore_msg, curses.color_pair(1))
        except Exception as e:
            error_msg = f"Error saving score: {e}"
            safe_addstr(stdscr, center_y, max(0, (width - len(error_msg)) // 2), 
                       error_msg, curses.color_pair(2))
    
    # Menu options
    menu_items = ["Play Again", "View Highscores", "Exit"]
    selected_option = 0
    
    # Menu handling
    while True:
        # Display menu items
        for i, item in enumerate(menu_items):
            y = center_y + 2 + i
            x = (width - len(item)) // 2
            if i == selected_option:
                safe_addstr(stdscr, y, x, item, curses.color_pair(4) | curses.A_BOLD)
            else:
                safe_addstr(stdscr, y, x, item)
        
        # Handle key presses
        stdscr.nodelay(False)  # Wait for key press
        key = stdscr.getch()
        
        if key == curses.KEY_UP and selected_option > 0:
            selected_option -= 1
        elif key == curses.KEY_DOWN and selected_option < len(menu_items) - 1:
            selected_option += 1
        elif key == 10:  # Enter key
            if menu_items[selected_option] == "Play Again":
                return "play_again"
            elif menu_items[selected_option] == "View Highscores":
                show_highscores(stdscr)
                stdscr.clear()
                # Redraw game over screen
                safe_addstr(stdscr, center_y - 4, max(0, (width - len(game_over_msg)) // 2), 
                           game_over_msg, curses.A_BOLD | curses.color_pair(2))
                safe_addstr(stdscr, center_y - 2, max(0, (width - len(score_msg)) // 2), 
                           score_msg, curses.color_pair(3))
            elif menu_items[selected_option] == "Exit":
                return "exit"

if __name__ == "__main__":
    try:
        # Initialize curses and database
        while True:
            result = curses.wrapper(main)
            if result != "play_again":
                break
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    except Exception as e:
        # Handle other exceptions
        curses.endwin()
        print(f"An error occurred: {e}")
    finally:
        # Ensure terminal is left in a good state
        curses.endwin()
        # Close database connection if still open
        if db.conn:
            db.close()
        print("Thanks for playing Snake!")
        print(f"Run 'python snake_game.py' to play again.")

