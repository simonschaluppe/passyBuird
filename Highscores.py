from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent
#sys.path.append(str(Path(__file__).parent.parent))
SCORE_PATH = ROOT_PATH / "passyBuird/assets/highscores.txt"

class Scoreboard:
    def __init__(self):
        self.scores = self.load_highscores()

    def add_score(self, name: str, score: int):
        scores.append((name, score))

    def top(self, n=None):
        # Sort by score descending
        ordered = sorted(scores, key=lambda x: x[1], reverse=True)
        return ordered if n is None else ordered[:n]

    def display(self, n=None):
        for i, (name, score) in enumerate(top(n), start=1):
            print(f"{i:2d}. {name:20s} {score}")
                
    def get_highscores(self):
        return self.scores
    
    def load_highscores(self):
        scores = open(SCORE_PATH)
        return scores