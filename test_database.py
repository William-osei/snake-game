#!/usr/bin/env python3
"""
Test script for the Snake Game Database Manager.
This script creates a test database and performs various operations to verify functionality.
"""

import os
import time
from datetime import datetime, timedelta
from database_manager import SnakeGameDatabaseManager


def print_section(title):
    """Print a formatted section title."""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50)


def main():
    """Main test function."""
    # Use a test database file
    test_db_file = "test_snake_game.db"
    
    # Remove the test database if it already exists
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
        print(f"Removed existing test database: {test_db_file}")
    
    print_section("Creating Database")
    db = SnakeGameDatabaseManager(test_db_file)
    print(f"Database created: {test_db_file}")
    
    # Connect to the database for the tests
    db.connect()
    
    # Test 1: Add default game settings
    print_section("Adding Game Settings")
    settings = [
        ("difficulty", "medium", "Game difficulty level (easy, medium, hard)"),
        ("speed", "10", "Snake movement speed"),
        ("board_width", "20", "Width of the game board"),
        ("board_height", "20", "Height of the game board"),
        ("food_value", "10", "Points gained when eating food"),
        ("special_food_value", "25", "Points gained when eating special food"),
        ("special_food_probability", "0.1", "Probability of spawning special food"),
        ("walls_enabled", "true", "Whether walls are enabled (if false, snake wraps around)"),
    ]
    
    for name, value, description in settings:
        setting_id = db.add_setting(name, value, description)
        print(f"Added setting: {name} = {value} (ID: {setting_id})")
    
    # Verify settings were added
    all_settings = db.get_all_settings()
    print(f"\nTotal settings: {len(all_settings)}")
    for setting in all_settings:
        print(f"  {setting['setting_name']}: {setting['setting_value']}")
    
    # Test 2: Add test players
    print_section("Adding Players")
    players = ["Player1", "Player2", "SnakeMaster", "AppleCatcher", "GameWizard"]
    player_ids = {}
    
    for username in players:
        player_id = db.add_player(username)
        player_ids[username] = player_id
        print(f"Added player: {username} (ID: {player_id})")
    
    # Verify players were added
    all_players = db.get_all_players()
    print(f"\nTotal players: {len(all_players)}")
    for player in all_players:
        print(f"  {player['username']} (ID: {player['id']}, Created: {player['creation_date']})")
    
    # Test 3: Record game sessions
    print_section("Recording Game Sessions")
    
    # Generate some sample game sessions
    now = datetime.now()
    game_sessions = [
        # Player1's games
        (player_ids["Player1"], 100, 60),  # 100 points in 60 seconds
        (player_ids["Player1"], 150, 90),  # 150 points in 90 seconds
        (player_ids["Player1"], 80, 45),   # 80 points in 45 seconds
        
        # Player2's games
        (player_ids["Player2"], 120, 70),  # 120 points in 70 seconds
        (player_ids["Player2"], 200, 110), # 200 points in 110 seconds
        
        # SnakeMaster's games (highest scores)
        (player_ids["SnakeMaster"], 250, 120),  # 250 points in 120 seconds
        (player_ids["SnakeMaster"], 300, 150),  # 300 points in 150 seconds
        
        # AppleCatcher's games
        (player_ids["AppleCatcher"], 180, 100),  # 180 points in 100 seconds
        
        # GameWizard's games
        (player_ids["GameWizard"], 220, 115),  # 220 points in 115 seconds
    ]
    
    # Add game sessions with different dates
    for i, (player_id, score, duration) in enumerate(game_sessions):
        # Spread the game sessions over the past week
        days_ago = i % 7  # 0 to 6 days ago
        game_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        
        session_id = db.add_game_session(player_id, score, duration, game_date)
        print(f"Added game session: Player {player_id}, Score: {score}, Duration: {duration}s, Date: {game_date} (ID: {session_id})")
    
    # Test 4: Retrieve player game history
    print_section("Player Game History")
    
    for username, player_id in player_ids.items():
        sessions = db.get_player_game_sessions(player_id)
        print(f"\n{username}'s game history ({len(sessions)} games):")
        
        for session in sessions:
            print(f"  Date: {session['date_played']}, Score: {session['score']}, Duration: {session['duration']}s")
    
    # Test 5: Retrieve and display highscores
    print_section("Highscores")
    
    highscores = db.get_highscores(limit=10)
    print("Top 10 Highscores:")
    
    for i, score in enumerate(highscores, 1):
        print(f"  {i}. {score['username']}: {score['score']} points (achieved on {score['date_achieved']})")
    
    # Test 6: Update a game setting
    print_section("Updating Game Settings")
    
    # Change the difficulty from medium to hard
    old_setting = db.get_setting("difficulty")
    print(f"Old difficulty setting: {old_setting['setting_value']}")
    
    db.add_setting("difficulty", "hard", "Game difficulty level (easy, medium, hard)")
    new_setting = db.get_setting("difficulty")
    print(f"New difficulty setting: {new_setting['setting_value']}")
    
    # Test 7: Player's highscore
    print_section("Player Highscores")
    
    for username, player_id in player_ids.items():
        highscore = db.get_player_highscore(player_id)
        if highscore:
            print(f"{username}'s highest score: {highscore['score']} points")
        else:
            print(f"{username} has no recorded highscores")
    
    # Clean up
    db.close()
    print_section("Test Completed Successfully")
    print(f"Database file: {test_db_file}")
    
    return 0


if __name__ == "__main__":
    main()

