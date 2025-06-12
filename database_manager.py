import sqlite3
import os
from datetime import datetime


class SnakeGameDatabaseManager:
    """
    A class to manage database operations for the Snake Game.
    Handles connections, table creation, and CRUD operations.
    """

    def __init__(self, db_file="snake_game.db"):
        """
        Initialize the database manager with a database file.
        
        Args:
            db_file (str): Path to the SQLite database file
        """
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        
        # Create tables on initialization if they don't exist
        self.connect()
        self.create_tables()
        self.close()

    def connect(self):
        """Establish a connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row  # This enables column access by name
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def create_tables(self):
        """Create all required tables if they don't exist."""
        if not self.conn:
            if not self.connect():
                return False
        
        # Player table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Game Session table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER NOT NULL,  -- in seconds
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
        )
        ''')
        
        # Create index on player_id for faster lookups
        self.cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_game_sessions_player_id ON game_sessions (player_id)
        ''')
        
        # Highscores table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS highscores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            date_achieved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
        )
        ''')
        
        # Create index on score for faster highscore lookups
        self.cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_highscores_score ON highscores (score DESC)
        ''')
        
        # Game Settings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            description TEXT
        )
        ''')
        
        self.conn.commit()
        return True
    
    # Player CRUD operations
    
    def add_player(self, username):
        """
        Add a new player to the database.
        
        Args:
            username (str): The player's username
            
        Returns:
            int: The ID of the newly created player, or None if failed
        """
        if not self.conn and not self.connect():
            return None
            
        try:
            self.cursor.execute(
                "INSERT INTO players (username) VALUES (?)",
                (username,)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding player: {e}")
            self.conn.rollback()
            return None
    
    def get_player(self, player_id=None, username=None):
        """
        Get a player by ID or username.
        
        Args:
            player_id (int, optional): The player's ID
            username (str, optional): The player's username
            
        Returns:
            dict: Player data or None if not found
        """
        if not self.conn and not self.connect():
            return None
            
        try:
            if player_id:
                self.cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
            elif username:
                self.cursor.execute("SELECT * FROM players WHERE username = ?", (username,))
            else:
                return None
                
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"Error getting player: {e}")
            return None
    
    def get_all_players(self):
        """
        Get all players from the database.
        
        Returns:
            list: List of player dictionaries
        """
        if not self.conn and not self.connect():
            return []
            
        try:
            self.cursor.execute("SELECT * FROM players")
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting players: {e}")
            return []
    
    def update_player(self, player_id, username):
        """
        Update a player's information.
        
        Args:
            player_id (int): The player's ID
            username (str): The new username
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.conn and not self.connect():
            return False
            
        try:
            self.cursor.execute(
                "UPDATE players SET username = ? WHERE id = ?",
                (username, player_id)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating player: {e}")
            self.conn.rollback()
            return False
    
    def delete_player(self, player_id):
        """
        Delete a player from the database.
        
        Args:
            player_id (int): The player's ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.conn and not self.connect():
            return False
            
        try:
            self.cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting player: {e}")
            self.conn.rollback()
            return False
    
    # Game Session CRUD operations
    
    def add_game_session(self, player_id, score, duration, date_played=None):
        """
        Add a new game session to the database.
        
        Args:
            player_id (int): The player's ID
            score (int): The score achieved in the game
            duration (int): The duration of the game in seconds
            date_played (str, optional): Date and time the game was played
            
        Returns:
            int: The ID of the newly created game session, or None if failed
        """
        if not self.conn and not self.connect():
            return None
            
        try:
            if date_played:
                self.cursor.execute(
                    "INSERT INTO game_sessions (player_id, score, duration, date_played) VALUES (?, ?, ?, ?)",
                    (player_id, score, duration, date_played)
                )
            else:
                self.cursor.execute(
                    "INSERT INTO game_sessions (player_id, score, duration) VALUES (?, ?, ?)",
                    (player_id, score, duration)
                )
            
            self.conn.commit()
            
            # Check if this is a high score for the player
            self._update_highscore(player_id, score)
            
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding game session: {e}")
            self.conn.rollback()
            return None
    
    def _update_highscore(self, player_id, score):
        """
        Update the highscores table if this is one of the top scores.
        
        Args:
            player_id (int): The player's ID
            score (int): The score achieved
        """
        try:
            # Get the player's current high score
            self.cursor.execute(
                "SELECT score FROM highscores WHERE player_id = ? ORDER BY score DESC LIMIT 1",
                (player_id,)
            )
            result = self.cursor.fetchone()
            
            if not result or score > result['score']:
                # This is a new high score for the player
                self.cursor.execute(
                    "INSERT INTO highscores (player_id, score) VALUES (?, ?)",
                    (player_id, score)
                )
                self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating highscore: {e}")
    
    def get_game_session(self, session_id):
        """
        Get a game session by ID.
        
        Args:
            session_id (int): The game session ID
            
        Returns:
            dict: Game session data or None if not found
        """
        if not self.conn and not self.connect():
            return None
            
        try:
            self.cursor.execute("SELECT * FROM game_sessions WHERE id = ?", (session_id,))
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"Error getting game session: {e}")
            return None
    
    def get_player_game_sessions(self, player_id):
        """
        Get all game sessions for a specific player.
        
        Args:
            player_id (int): The player's ID
            
        Returns:
            list: List of game session dictionaries
        """
        if not self.conn and not self.connect():
            return []
            
        try:
            self.cursor.execute(
                "SELECT * FROM game_sessions WHERE player_id = ? ORDER BY date_played DESC", 
                (player_id,)
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting player game sessions: {e}")
            return []
    
    def delete_game_session(self, session_id):
        """
        Delete a game session from the database.
        
        Args:
            session_id (int): The game session ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.conn and not self.connect():
            return False
            
        try:
            self.cursor.execute("DELETE FROM game_sessions WHERE id = ?", (session_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting game session: {e}")
            self.conn.rollback()
            return False
    
    # Highscore operations
    
    def get_highscores(self, limit=10):
        """
        Get the top highscores from the database.
        
        Args:
            limit (int): Maximum number of highscores to return
            
        Returns:
            list: List of highscore dictionaries with player information
        """
        if not self.conn and not self.connect():
            return []
            
        try:
            self.cursor.execute(
                """
                SELECT h.id, h.player_id, h.score, h.date_achieved, p.username
                FROM highscores h
                JOIN players p ON h.player_id = p.id
                ORDER BY h.score DESC
                LIMIT ?
                """, 
                (limit,)
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting highscores: {e}")
            return []
    
    def get_player_highscore(self, player_id):
        """
        Get the highest score for a specific player.
        
        Args:
            player_id (int): The player's ID
            
        Returns:
            dict: Highscore data or None if not found
        """
        if not self.conn and not self.connect():
            return None
            
        try:
            self.cursor.execute(
                "SELECT * FROM highscores WHERE player_id = ? ORDER BY score DESC LIMIT 1", 
                (player_id,)
            )
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"Error getting player highscore: {e}")
            return None
    
    # Game Settings operations
    
    def add_setting(self, setting_name, setting_value, description=None):
        """
        Add or update a game setting.
        
        Args:
            setting_name (str): The name of the setting
            setting_value (str): The value of the setting
            description (str, optional): A description of the setting
            
        Returns:
            int: The ID of the newly created setting, or None if failed
        """
        if not self.conn and not self.connect():
            return None
            
        try:
            # Check if setting already exists
            self.cursor.execute("SELECT id FROM game_settings WHERE setting_name = ?", (setting_name,))
            result = self.cursor.fetchone()
            
            if result:
                # Update existing setting
                if description:
                    self.cursor.execute(
                        "UPDATE game_settings SET setting_value = ?, description = ? WHERE id = ?",
                        (setting_value, description, result['id'])
                    )
                else:
                    self.cursor.execute(
                        "UPDATE game_settings SET setting_value = ? WHERE id = ?",
                        (setting_value, result['id'])
                    )
                self.conn.commit()
                return result['id']
            else:
                # Insert new setting
                self.cursor.execute(
                    "INSERT INTO game_settings (setting_name, setting_value, description) VALUES (?, ?, ?)",
                    (setting_name, setting_value, description)
                )
                self.conn.commit()
                return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding/updating setting: {e}")
            self.conn.rollback()
            return None
    
    def get_setting(self, setting_name):
        """
        Get a game setting by name.
        
        Args:
            setting_name (str): The name of the setting
            
        Returns:
            dict: Setting data or None if not found
        """
        if not self.conn and not self.connect():
            return None
            
        try:
            self.cursor.execute("SELECT * FROM game_settings WHERE setting_name = ?", (setting_name,))
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"Error getting setting: {e}")
            return None
    
    def get_all_settings(self):
        """
        Get all game settings.
        
        Returns:
            list: List of setting dictionaries
        """
        if not self.conn and not self.connect():
            return []
            
        try:
            self.cursor.execute("SELECT * FROM game_settings")
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting settings: {e}")
            return []
    
    def delete_setting(self, setting_name):
        """
        Delete a game setting.
        
        Args:
            setting_name (str): The name of the setting
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.conn and not self.connect():
            return False
            
        try:
            self.cursor.execute("DELETE FROM game_settings WHERE setting_name = ?", (setting_name,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting setting: {e}")
            self.conn.rollback()
            return False

