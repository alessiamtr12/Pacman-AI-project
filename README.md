# Pacman AI project

This project implements the Pacman game, enhanced with a set of **Artificial Intelligence** algorithms. This was a team project and I was one of the members. This game has a winter theme and also has some funny features concerning Horia Brenciu singer.

---

## Game modes
### 1. Manual Mode
The classical way of playing the original game. The pacman is controlled by arrows and the ghosts have 3 states like in the original game: chasing, scattering and frightened. The player can choose one of the following chasing algorithms for the ghosts.
* **Depth-First Search** (DFS)
* **Breadth-First Search** (BFS)
* A*(with Manhattan heuritic)
### 2. Autonomous Mode
In this mode, Pacman plays himself. You can select different AI paradigms to see how they perform against the ghosts:
* **Reflex agent**: Instant decision-making based on immediate surroundings.
* **MinMax**:  Treats the game as an adversarial search problem, in which Pacman competes against ghosts. Pacman tries to maximize its score, while ghosts act as adversaries trying to minimize it, by forcing Pacman into losing situations.
* **Alpha-Beta Pruning**: An optimization of MinMax.
### 3. Alternate (Ghost) Mode
In this mode, you can play as Clyde. Pacman is controlled by MinMax algorithm.

---
## Unique Features
* Magic Chimney: Magic chimneys are randomly generated and if Pacman falls into it while in manual mode, the controls are swapped.
* Path Visualization: By pressing key 'P' you can see the the real-time paths that ghosts follow based on the chosen algorithm.
* Winter Theme: The ghosts and Pacman have a Christmassy look, having Santa hats. Also the pellets are replaced by snowflakes and the colors are changed from the original game to have a winter theme.
* Sounds and Effects: The song 'Noapte de Craciun' by Horia Brenciu plays in the background and a photo of the singer appears depending on the game ending. (Play the game to see them :) )


---

## Requirements & Installation

* **Language:** Python 3.x
* **Libraries:** Pygame (No external AI libraries like TensorFlow/PyTorch were used).

```bash
# Clone the repository
git clone https://github.com/alessiamtr12/Pacman-AI-project.git

# Install dependencies
pip install pygame

# Run the application
python main.py
