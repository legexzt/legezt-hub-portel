# Neon Runner (Python + Pyglet)

A fast neon lane-runner built with Python using Pyglet 2.x. It features crisp neon lines, simple jump physics, obstacles, score, pause, and mouse/touch-friendly input zones.

## Install

1) Optional: create and activate a virtual environment

Windows PowerShell:

```
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

2) Install dependencies

```
pip install -r python_game/requirements.txt
```

## Run

```
python python_game/main.py
```

Controls:
- `A/D` or `Left/Right` — change lane
- `Space/Up` — jump
- `Esc` — pause/resume; on Game Over, `R` to retry, `Esc` to return to menu

Mouse/touch:
- Tap/click top area to jump
- Tap/click bottom-left/right to switch lanes

## Assets

- Sound effect `hit.wav` is auto-downloaded at first run from CC0 sources to `python_game/assets/sfx/`.

## Notes

- Requires a working OpenGL driver (most Windows PCs are fine). If you see issues, update graphics drivers.
