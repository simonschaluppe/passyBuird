import json
from pathlib import Path
from typing import Dict, List, Tuple

ROOT_PATH = Path(__file__).parent.parent
#sys.path.append(str(Path(__file__).parent.parent))
SCORE_PATH = ROOT_PATH / "passyBuird/data/highscores.txt"

class Scoreboard:
    def __init__(self, path: Path = SCORE_PATH):
        self.path = Path(path)
        self.scores: List[Tuple[str,int]] = self.load_highscores()
        print(self.get_highscores())

    def add_score(self, name: str, score: int) -> None:
        self.scores.append((name, int(score)))
        self.save_highscores()

    def top(self, n: int | None = None) -> List[Tuple[str, int]]:
        if n > len(self.scores): 
            n = len(self.scores)
        ordered = sorted(self.scores, key=lambda x: x[1], reverse=True)
        return ordered if n is None else ordered[:n]

    def display(self, n: int | None = None) -> None:
        for i, (name, score) in enumerate(self.top(n), start=1):
            print(f"{i:2d}. {name:20s} {score}")

    def get_highscores(self) -> List[Tuple[str, int]]:
        return [f"{i:2d}. {name:20s} {score}" for i, (name, score) in enumerate(self.top(10), start=1)]  # return a copy to avoid external mutation

    def load_highscores(self) -> List[Tuple[str, int]]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            # Expecting list of [name, score] pairs or list of dicts
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    return [(d["name"], int(d["score"])) for d in data]
                return [(name, int(score)) for name, score in data]
        except Exception:
            pass
        return []

    def save_highscores(self) -> None:
        # Save as list of dicts for clarity
        data = [{"name": n, "score": s} for n, s in self.scores]
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    sb = Scoreboard("data/highscores.txt")
    sb.add_score("Simon", 430)
    sb.display()
    print(sb.get_highscores())