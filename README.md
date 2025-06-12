# 🐍 Classic Snake Game

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-4CAF50?style=for-the-badge)](https://william-osei.github.io/snake-game)
[![Repository](https://img.shields.io/badge/📁_Repository-2196F3?style=for-the-badge)](https://github.com/William-osei/snake-game)

A classic Snake game implementation available in both Python (with GUI) and HTML5/JavaScript versions. Features smooth gameplay, progressive difficulty, score tracking, and collision detection algorithms.

## 🎮 Features

- **Dual Implementation**: Python GUI version and Web-based HTML5 version
- **Smooth Gameplay**: Responsive controls and fluid movement
- **Progressive Difficulty**: Game speed increases as you score
- **Score Tracking**: Local high score storage and statistics
- **Collision Detection**: Advanced algorithms for precise game mechanics
- **Database Integration**: SQLite database for score persistence (Python version)
- **Responsive Design**: Web version adapts to different screen sizes

## 🚀 How to Play

### Python Version
1. Install Python 3.x
2. Install required dependencies: `pip install pygame sqlite3`
3. Run: `python snake_game.py`
4. Use arrow keys to control the snake
5. Eat food to grow and increase your score
6. Avoid hitting walls or yourself!

### Web Version
1. Open `snake-game.html` in any modern web browser
2. Use arrow keys or WASD to control the snake
3. Click "Start Game" to begin
4. Your high score is saved locally

## 🛠️ Tech Stack

### Python Version
- **Python 3.x**: Core game logic
- **Pygame**: Graphics and game loop
- **SQLite3**: Database for score management
- **Object-Oriented Design**: Clean, maintainable code structure

### Web Version
- **HTML5 Canvas**: Game rendering
- **JavaScript ES6+**: Game logic and controls
- **CSS3**: Styling and responsive design
- **Local Storage**: High score persistence

## 📁 Project Structure

```
snake-game/
├── snake_game.py           # Main Python game file
├── database_manager.py     # Database operations
├── test_database.py        # Database testing
├── index.html              # Web version (main)
├── snake-game.html         # Alternative web version
├── test_snake_game.db      # SQLite database
├── LICENSE                 # MIT License
└── README.md              # Project documentation
```

## 🎯 Game Mechanics

### Core Features
- **Snake Movement**: Continuous movement with direction changes
- **Food Generation**: Random food placement with collision detection
- **Growth System**: Snake grows when consuming food
- **Boundary Detection**: Game over when hitting walls
- **Self-Collision**: Game over when snake hits itself
- **Score System**: Points awarded for each food consumed

### Advanced Features
- **Speed Progression**: Game speeds up as score increases
- **High Score Tracking**: Persistent storage of best scores
- **Game Statistics**: Track games played, best score, average score
- **Smooth Graphics**: Anti-aliased rendering and smooth animations

## 🏗️ Development

### Python Version Architecture
- **Game Class**: Main game logic and state management
- **Snake Class**: Snake entity with movement and growth
- **Food Class**: Food generation and collision detection
- **Database Manager**: Score persistence and statistics
- **Event Handling**: Keyboard input and game events

### Web Version Architecture
- **Canvas Rendering**: HTML5 Canvas for game graphics
- **Game Loop**: RequestAnimationFrame for smooth gameplay
- **Input Handling**: Keyboard event listeners
- **State Management**: Game state transitions and scoring

## 📊 Database Schema (Python Version)

```sql
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Testing

Run the database tests:
```bash
python test_database.py
```

## 🎨 Screenshots

*Screenshots and gameplay GIFs would go here*

## 🚀 Future Enhancements

- [ ] Multiplayer mode
- [ ] Power-ups and special items
- [ ] Different game modes (time attack, survival)
- [ ] Mobile touch controls
- [ ] Sound effects and background music
- [ ] Leaderboard system
- [ ] Custom themes and skins

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**William Osei Aborah**
- GitHub: [@William-osei](https://github.com/William-osei)
- Portfolio: [william-osei.github.io/portfolio](https://william-osei.github.io/portfolio)

---

⭐ If you enjoyed this project, please give it a star!

