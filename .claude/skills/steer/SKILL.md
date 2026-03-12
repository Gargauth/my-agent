---
name: steer
description: GUI automation CLI. Use steer to see the screen, click elements, type text, send hotkeys, scroll, drag, manage windows and apps, run OCR on Electron apps, and wait for UI conditions. Works on macOS (Swift) and Linux/Hyprland (Python).
---

# Steer — GUI Automation

## Platform Detection

Detect your platform first and set the correct steer command:

```bash
if [ "$(uname -s)" = "Linux" ]; then
  # Linux (Hyprland) — Python CLI
  STEER="cd /path/to/repo/apps/steer-linux && uv run python main.py"
else
  # macOS — Swift binary
  STEER="apps/steer/.build/release/steer"
fi
```

**On Linux**, every steer invocation looks like:
```bash
cd /path/to/repo/apps/steer-linux && uv run python main.py <command> [flags]
```

**On macOS**, every steer invocation looks like:
```bash
steer <command> [flags]
```

Run `<steer> --help` and `<steer> <command> --help` to learn flags.

## Commands

| Command     | Purpose                                                                                                                                                                                                    |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `see`       | Takes a screenshot (PNG) and walks the accessibility tree. Screenshot always succeeds. Elements are best-effort — may be empty for Electron apps. Pass `--ocr` to fall back to OCR when the tree is empty. |
| `click`     | Click by element ID, label, or coordinates                                                                                                                                                                 |
| `type`      | Type text into focused element or a target                                                                                                                                                                 |
| `hotkey`    | Keyboard shortcuts (super+s, return, escape, etc.)                                                                                                                                                         |
| `scroll`    | Scroll up/down/left/right                                                                                                                                                                                  |
| `drag`      | Drag between elements or coordinates                                                                                                                                                                       |
| `apps`      | List, launch, or activate apps                                                                                                                                                                             |
| `screens`   | List displays with resolution and scale                                                                                                                                                                    |
| `window`    | Move, resize, fullscreen, close windows                                                                                                                                                                    |
| `ocr`       | Takes a screenshot and runs OCR. Returns text with x/y positions. Use `--store` to make results clickable (O1, O2, etc.). Use when `see` returns no elements.                                              |
| `focus`     | Show currently focused element                                                                                                                                                                             |
| `find`      | Search elements by text in latest snapshot                                                                                                                                                                 |
| `clipboard` | Read/write system clipboard                                                                                                                                                                                |
| `wait`      | Wait for app launch or element to appear                                                                                                                                                                   |

Always pass `--json` for structured output.

## Linux Key Mapping

On Linux, modifier keys differ from macOS:

| macOS       | Linux         | When to use                              |
| ----------- | ------------- | ---------------------------------------- |
| `cmd`       | `super`       | Window manager shortcuts                 |
| `cmd+c/v/x` | `ctrl+c/v/x` | Copy, paste, cut (in most apps)         |
| `cmd+s`     | `ctrl+s`      | Save                                     |
| `cmd+a`     | `ctrl+a`      | Select all                               |
| `cmd+shift` | `super+shift` | WM shortcuts with shift                  |

Use `ctrl` for app shortcuts (save, copy, paste). Use `super` for window manager actions.

## How to Work

You are controlling a real desktop. You cannot see anything unless you explicitly look. You cannot assume anything worked unless you verify.

### 1. Know your environment first

Before doing anything, understand the display setup, what's running, and capture the current state:

```
<steer> screens --json       → which monitors exist, their resolution
<steer> apps --json          → what apps are running
<steer> see --screen 0 --json  → screenshot of screen 0 (primary)
```

Take a screenshot of **each screen** returned by `screens`. Read them. This gives you a baseline.

### 2. Focus the app, then verify

Before interacting with any app, make sure it's the active window:

```
<steer> apps activate Firefox --json
<steer> see --app Firefox --json        → verify it's in front, read the state
```

### 3. One action, then observe

**NEVER chain multiple steer commands in one bash call.** The screen changes after every action. You must look after every action.

The loop is:

1. `<steer> see` — look at the screen
2. Read the JSON — understand what you see
3. Do ONE action (click, type, hotkey, scroll)
4. `<steer> see` — look again to confirm it worked
5. Repeat

### 4. Clicking safely

Before clicking anything:

- Run `<steer> see --app <app> --json` to get a fresh snapshot
- Use element IDs from the snapshot (B1, T1, L3) — not coordinates when possible
- After clicking, run `<steer> see` again to confirm the click landed

### 5. Typing into fields

- Before typing: ALWAYS check focus with `<steer> focus --json`
- Use `<steer> type "text" --into T1 --json` to click-then-type
- After typing, verify with `<steer> see`
- For URLs in browsers: type URL, then `<steer> hotkey return --json`, then `<steer> see`

### 6. Reading content from apps

Both `see` and `ocr` save a screenshot PNG (path in JSON `"screenshot"`). Read the image to inspect.

**Native apps**: `<steer> see --app <name> --json` gives the accessibility tree.

**Electron apps** (VS Code, Slack): Accessibility trees are empty. Use OCR:

```
<steer> ocr --app "Code" --store --json
```

With `--store`, OCR results become clickable elements (O1, O2, etc.).

### 7. Waiting for things

Don't assume the UI is ready. Use `<steer> wait`:

```
<steer> wait --app Firefox --json                    → wait for app to launch
<steer> wait --for "Submit" --app Firefox --json     → wait for element to appear
```

### 8. Multi-monitor awareness

If there are multiple screens, always check `<steer> screens --json` first and use `--screen <index>` when needed.

## Element IDs

Elements from `see` get role-based IDs: **B** (button), **T** (text field), **S** (static text), **I** (image), **C** (checkbox), **L** (link), **M** (menu item), **O** (OCR element), etc.

IDs regenerate with each snapshot. Always use IDs from the most recent `see` or `ocr --store`.

## Rules

- **One command per bash call** — never chain steer commands
- **Always verify** — `see` after every action
- **Focus first** — activate the app before interacting
- **Know your screens** — check `screens` before clicking
- **Use `--json` always** — structured output is reliable
- **Write all files to /tmp** — never write output files into the project directory
- **Run `<steer> <cmd> --help`** if you're unsure about a command's flags
