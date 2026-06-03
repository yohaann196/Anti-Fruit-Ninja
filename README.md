# Anti Fruit Ninja

A dark comedy game where you are the villain. The fruits have names, families, feelings, podcasts, etc. They have a life! You ruthlessly kill them anyway. Or... maybe you don't.

All visuals are drawn in code — they are intentionally crude, there are no image assets.

## How to Play

```
pip install -r requirements.txt
python game.py
```

Requires Python 3.7+ and PyGame.

Move your mouse over fruits to slice them. Each slice is a sin. Letting a fruit pass earns mercy. The game tracks both and judges you accordingly.

## Controls

| Key | Action |
|-----|--------|
| Mouse | Slice fruits by moving cursor over them |
| Enter/Space | Start game from title screen |
| Escape | Pause/unpause |
| R | Restart after an ending |

## Endings

The game has **5 endings**. Each ending screen tells you which ending you got, whether it's good or bad, and how you triggered it.

| # | Ending | Type | How to get it |
|---|--------|------|---------------|
| 1 | **Forgiveness** | ✅ Best | Let 50 fruits pass without slicing (reach 50 mercy) |
| 2 | **Peaceful** | ✅ Good | Slice the grey willing fruit that says "i'm ready. please." |
| 3 | **Existential** | ⚪ Neutral | Slice 3 willing fruits — the game questions why |
| 4 | **Shame** | ❌ Bad | Reach 100 sins and then stop slicing — the fruits go on strike |
| 5 | **Addiction** | ❌ Worst | Reach 300 sins — the screen cracks, you can't stop |

There is also a **mid-game event** (not a full ending): at 200 sins, you receive a letter from Brenda Jr., the daughter of a watermelon you sliced. The game continues after the letter.

> **Note:** After 100 sins, fruits keep spawning. If you stop slicing and let all remaining fruits fall, the Shame ending triggers. If you keep slicing, you'll see the Brenda Jr. letter at 200 sins and eventually reach the Addiction ending at 300.

## Features

- Fruits have names, backstories, and they remember what you did
- You can go on bloody rampages and combo attacks, killing the innocent fruits.
- Screen shake, vignette, and color shift as your sins pile up
- Cursor trail turns red as you descend into fruit murder
- Mercy milestones reward you with flowers, rainbows, and gratitude
- Documentarians show up to film your crimes; lawyers serve you papers
- Persistent guilt... lifetime sins are saved and shown on the title screen

## Technical Notes

- Built with PyGame
- Single-file game (`game.py`) — all visuals drawn programmatically, no image files
- 60 FPS with frame-rate-independent physics
- Save data stored in `~/.anti_fruit_ninja_save.json`

## Fonts

Fonts use [Comic Neue](https://github.com/crozynski/comicneue) by Craig Rozynski, licensed under the [SIL Open Font License](fonts/OFL.txt).

## Credits:
check out [the original repo](https://github.com/zenilharia26/Fruit-Ninja) upon which I built this project!
