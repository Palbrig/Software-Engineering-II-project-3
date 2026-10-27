import "css/style.css";

const games = [
  { title: "Minesweeper", description: "Coming soon!" },
  { title: "Puzzle Game", description: "Coming soon!" }
];

const gameList = document.querySelector("#game-list");

for (const game of games) {
  const card = document.createElement("article");
  card.className = "game-card";

  const title = document.createElement("h3");
  title.textContent = game.title;

  const description = document.createElement("p");
  description.textContent = game.description;

  card.append(title, description);
  gameList.append(card);
}