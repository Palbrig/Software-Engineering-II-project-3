// Add one entry per game. Use the same id for its folder in public/builds/.
export const games = [
  {
    id: "minesweeper",
    title: "Minesweeper",
    description: "Use numbered clues to uncover safe tiles without hitting a mine.",
    goal: "Reveal every safe tile.",
    controls: "Click to reveal a tile. Right-click to mark a suspected mine.",
    rules: "A number counts the mines in the eight surrounding positions. Revealing a mine ends the game."
  },
  {
    id: "snake",
    title: "Snake",
    description: "Guide the snake around the grid, collect food, and grow without crashing.",
    goal: "Eat as much food as possible and achieve the highest score.",
    controls: "Use the Arrow Keys or WASD to move. Press P to pause and resume.",
    rules: "Collect yellow food to grow and increase your score. Avoid hitting the walls or your own body. The game gradually speeds up as your score increases."
  },
  {
    id: "connect4",
    title: "Connect Four",
    description: "[Placeholder]",
    goal: "[Placeholder]",
    controls: "[Placeholder]",
    rules: "[Placeholder]"
  },
  {
    id: "tetris",
    title: "Tetris",
    description: "Make full lines of tiles with the falling blocks to clear lines and rack up a high score.",
    goal: "Clear as many lines as you can to try and get the highest score.",
    controls: "Use the left and right arrow keys to move the falling blocks. Use up to rotate them and down to make them fall faster for more points.",
    rules: "Clear the board by filling all of a row's tiles. The pieces fall faster as your score goes higher."
  },
  {
    id: "sudoku",
    title: "Sudoku",
    description: "A Sudoku puzzle game with three difficulty levels: Easy, Medium, and Hard. Players can generate new puzzles and check their answers.",
    goal: "Complete the 9x9 Sudoku grid by filling in the missing numbers correctly.",
    controls: "Select a difficulty level, click an empty cell, and enter a number from 1 to 9. Use the New Game button to start another puzzle and the Check Answer button to check your solution.",
    rules: "Fill every row, column, and 3x3 box with the numbers 1 through 9 without repeating any number. The puzzle is complete when all cells are filled correctly."
  }
];
