---
name: steer
description: Linux GUI automation CLI (Hyprland). Use steer to see the screen, click elements, type text, send hotkeys, scroll, drag, manage windows and apps, run OCR, and wait for UI conditions.
---

# Steer — Linux GUI Automation (Hyprland)

Command: `cd apps/steer-linux && uv run python main.py <command> [flags]`

Run `cd apps/steer-linux && uv run python main.py --help` to see all commands.
Run `cd apps/steer-linux && uv run python main.py <command> --help` to see flags.

## Commands

| Command     | Purpose                                                                                                                                                                |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `see`       | Screenshot (PNG) + accessibility tree. Elements may be empty for Electron apps. Pass `--ocr` to fall back to OCR when the tree is empty.                               |
| `click`     | Click by element ID, label, or coordinates                                                                                                                             |
| `type`      | Type text into focused element or a target                                                                                                                             |
| `hotkey`    | Keyboard shortcuts (super+l, ctrl+s, return, escape, etc.)                                                                                                             |
| `scroll`    | Scroll up/down/left/right                                                                                                                                              |
| `drag`      | Drag between elements or coordinates                                                                                                                                   |
| `apps`      | List, launch, or activate apps                                                                                                                                         |
| `screens`   | List displays with resolution and scale                                                                                                                                |
| `window`    | Move, resize, fullscreen, close windows                                                                                                                                |
| `ocr`       | Screenshot + Tesseract OCR. Returns text with x/y positions. Use `--store` to make results clickable (O1, O2, etc.). Use when `see` returns no elements.               |
| `focus`     | Show currently focused element                                                                                                                                         |
| `find`      | Search elements by text in latest snapshot                                                                                                                             |
| `clipboard` | Read/write system clipboard (wl-clipboard)                                                                                                                             |
| `wait`      | Wait for app launch or element to appear                                                                                                                               |

Always pass `--json` for structured output.

## Key Mapping

| Keys            | Use for                                  |
| --------------- | ---------------------------------------- |
| `ctrl+c/v/x`   | Copy, paste, cut                         |
| `ctrl+s`        | Save                                     |
| `ctrl+a`        | Select all                               |
| `super`         | Hyprland WM shortcuts                    |
| `super+shift`   | WM shortcuts with shift                  |

Use `ctrl` for app shortcuts. Use `super` for window manager actions.

## How to Work

You are controlling a real Linux/Hyprland desktop. You cannot see anything unless you explicitly look. You cannot assume anything worked unless you verify.

### 1. Know your environment first

```bash
cd apps/steer-linux && uv run python main.py screens --json
cd apps/steer-linux && uv run python main.py apps --json
cd apps/steer-linux && uv run python main.py see --screen 0 --json
```

Take a screenshot of **each screen**. Read them. This gives you a baseline.

### 2. Focus the app, then verify

```bash
cd apps/steer-linux && uv run python main.py apps activate firefox --json
cd apps/steer-linux && uv run python main.py see --app firefox --json
```

### 3. One action, then observe

**NEVER chain multiple steer commands in one bash call.** The screen changes after every action.

The loop is:

1. `see` — look at the screen
2. Read the JSON — understand what you see
3. Do ONE action (click, type, hotkey, scroll)
4. `see` — look again to confirm it worked
5. Repeat

### 4. Clicking safely

- Run `see --app <app> --json` to get a fresh snapshot
- Use element IDs (B1, T1, L3) — not coordinates when possible
- After clicking, run `see` again to confirm

### 5. Typing into fields

- Check focus with `focus --json` first
- Use `type "text" --into T1 --json` to click-then-type
- After typing, verify with `see`

### 6. Reading content from apps

Both `see` and `ocr` save a screenshot PNG (path in JSON `"screenshot"`).

**Native GTK/Qt apps**: `see --app <name> --json` gives accessibility tree.

**Electron apps** (VS Code, Slack): Use OCR:

```bash
cd apps/steer-linux && uv run python main.py ocr --app "Code" --store --json
```

With `--store`, OCR results become clickable elements (O1, O2, etc.).

### 7. Waiting for things

```bash
cd apps/steer-linux && uv run python main.py wait --app firefox --json
cd apps/steer-linux && uv run python main.py wait --for "Submit" --app firefox --json
```

### 8. Multi-monitor

Check `screens --json` first and use `--screen <index>` when needed.

## Element IDs

Role-based IDs: **B** (button), **T** (text field), **S** (static text), **I** (image), **C** (checkbox), **L** (link), **M** (menu item), **O** (OCR element), etc.

IDs regenerate with each snapshot. Always use IDs from the most recent `see` or `ocr --store`.

## Rules

- **One command per bash call** — never chain steer commands
- **Always verify** — `see` after every action
- **Focus first** — activate the app before interacting
- **Know your screens** — check `screens` before clicking
- **Use `--json` always** — structured output is reliable
- **Write all files to /tmp** — never write into the project directory
- **Run `<command> --help`** if unsure about flags

## System Dependencies

```bash
sudo pacman -S tesseract tesseract-data-eng grim ydotool wl-clipboard wtype python-atspi jq
systemctl --user enable --now ydotoold
sudo usermod -aG input $USER
```
