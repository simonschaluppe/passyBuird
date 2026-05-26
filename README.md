
# PassyBuird

**PassyBuird** is a playful serious game about buildings, energy, comfort, and the noble art of not freezing, overheating, or going bankrupt.

You are in charge of a small building energy system. Outside, the weather does whatever it wants. Inside, people expect comfort. In between: walls, windows, ventilation, solar gains, heating, cooling, PV panels, a battery, the electricity grid, feed-in tariffs, CO₂ emissions, and your wallet.

The game turns building physics into something playable. Every simulated hour, the building gains and loses heat, indoor temperature changes, electricity is produced or bought, PV is used or fed into the grid, and your decisions affect comfort, money, and emissions.

Keep the house comfortable. Use your own solar power. Buy as little grid electricity as possible. Feed in what you cannot use. Survive the levels.

<img width="1280" height="720" alt="Screenshot 26-05-26_17-33-17" src="https://github.com/user-attachments/assets/a4accc7f-89c1-41f3-ba94-f09e3c1623ee" />


## What is this?

PassyBuird is a **serious game for exploring building energy behaviour**.

It shows how heating and cooling demand are connected to:

- outdoor temperature
- building envelope quality
- ventilation losses
- solar gains
- internal gains
- heat pump efficiency
- PV production
- battery storage
- grid electricity
- feed-in
- energy costs
- CO₂ emissions
- comfort limits

In short: a tiny playable heat balance with a tiny playable electricity system attached.

## Features

- Hourly building energy simulation
- Physical thermal energy flows:
  - transmission losses
  - ventilation losses
  - solar gains
  - internal gains
  - heating
  - cooling
- User-controlled heating and cooling
- Indoor comfort range and comfort score
- Level-based gameplay with different seasons and challenges
- PV electricity production from hourly profiles
- PV self-consumption
- Battery charging and discharging
- Grid electricity demand when PV and battery are not enough
- Feed-in of unused PV electricity
- Energy costs based on grid purchase and feed-in revenue
- CO₂ emissions based on electricity use and CO₂ intensity
- Upgrade shop for:
  - insulation
  - heating/cooling power
  - heat pump efficiency
  - electricity price discount
  - PV installation
- Highscore screen
- Music and sound effects
- Pixel-art inspired visuals
- Built with Python and pygame-ce

## Gameplay

Each level simulates a selected period of the year in hourly time steps.

At every step, the building reacts to weather, thermal losses, solar gains, internal gains, and your heating or cooling actions.

The basic logic is:

```text
weather + building envelope + usage
→ heat gains and heat losses
→ indoor temperature
→ heating or cooling demand
→ electricity demand
→ PV self-consumption / battery / grid / feed-in
→ money, CO₂, and comfort score
````

Your goal is to keep the building inside the comfort zone without burning through your budget.

You lose if comfort collapses or the money runs out.

You win a level by surviving until the end of the simulated period.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/simonschaluppe/passyBuird.git
cd passyBuird
````

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The required Python packages are listed in `requirements.txt`. The game uses `pygame-ce` for rendering and interaction, and additional packages for data handling, plotting, and Excel input files.


## Run the game

From the project root:

```bash
python game.py
```

## Controls

### General controls

| Key / Input | Action                                      |
| ----------- | ------------------------------------------- |
| Mouse       | Click buttons and shop items                |
| `Enter`     | Start / continue on menus and popup screens |
| `Q`         | Quit game                                   |
| `M`         | Toggle audio                                |
| `S`         | Take screenshot                             |

### Level controls

| Key / Input                  | Action                            |
| ---------------------------- | --------------------------------- |
| Left mouse button            | Heat                              |
| Right mouse button           | Cool                              |
| `Up Arrow`                   | Heat                              |
| `Down Arrow`                 | Cool                              |
| `P`                          | Pause / unpause                   |
| `A`                          | Toggle autopilot                  |
| `Esc`                        | Open shop                         |
| `1`                          | Simulation speed: 12 hours/second |
| `2`                          | Simulation speed: 24 hours/second |
| `3`                          | Simulation speed: 1 week/second   |
| `4`                          | Simulation speed: 2 weeks/second  |
| `5`                          | Simulation speed: 4 weeks/second  |
| Mouse wheel                  | Zoom camera                       |
| `Left Arrow` / `Right Arrow` | Move camera                       |
| `R`                          | Reset camera                      |

### Debug / demo controls

| Key | Action                 |
| --- | ---------------------- |
| `W` | Win current level      |
| `V` | Jump to victory screen |
| `D` | Toggle debug mode      |

## Project structure

```text
passyBuird/
├── game.py              # Main game loop and screen setup
├── settings.py          # Game settings and UI constants
├── levels.py            # Level definitions
├── upgrades.py          # Upgrade definitions
├── Highscores.py        # Highscore handling
├── renderer.py          # Drawing and visualization logic
├── handler.py           # Input handling, buttons, text input
├── camera.py            # Camera and zoom utilities
├── music.py             # Music and sound effects
├── particles.py         # Heating, cooling, purchase, and success effects
├── font.py              # Font helpers
├── utils.py             # Utility functions
├── model/               # Building and energy simulation model
│   ├── Simulation.py
│   ├── GameModel.py
│   ├── Building.py
│   ├── Comfort.py
│   ├── PV.py
│   ├── Battery.py
│   └── conversion.py
├── data/                # Weather, PV, building, usage, and CO₂ input data
├── assets/              # Images, fonts, sounds, backgrounds
├── language/            # UI/game text
└── Screenshots/         # Saved screenshots
```



[1]: https://github.com/simonschaluppe/passyBuird/blob/dev_open_day/game.py "passyBuird/game.py at dev_open_day · simonschaluppe/passyBuird · GitHub"
