# Tmux Shortcuts

Default prefix: `Ctrl+b`

## Sessions

| Key | Action |
|-----|--------|
| `tmux new -s name` | New named session |
| `tmux ls` | List sessions |
| `tmux attach -t name` | Attach to session |
| `prefix $` | Rename session |
| `prefix d` | Detach |
| `prefix s` | List/switch sessions |
| `prefix (` / `)` | Previous / next session |

## Windows (Tabs)

| Key | Action |
|-----|--------|
| `prefix c` | New window |
| `prefix ,` | Rename window |
| `prefix w` | List/switch windows |
| `prefix n` / `p` | Next / previous window |
| `prefix 0-9` | Switch to window by number |
| `prefix &` | Kill window |

## Panes

| Key | Action |
|-----|--------|
| `prefix %` | Split vertically |
| `prefix "` | Split horizontally |
| `prefix arrow` | Move between panes |
| `prefix q` | Show pane numbers |
| `prefix z` | Toggle pane zoom |
| `prefix {` / `}` | Swap pane left / right |
| `prefix x` | Kill pane |
| `prefix !` | Break pane into new window |
| `prefix Ctrl+arrow` | Resize pane |

## Copy Mode

| Key | Action |
|-----|--------|
| `prefix [` | Enter copy mode |
| `Space` | Start selection |
| `Enter` | Copy selection |
| `prefix ]` | Paste |
| `q` | Exit copy mode |

## Misc

| Key | Action |
|-----|--------|
| `prefix :` | Command prompt |
| `prefix ?` | List all keybindings |
| `prefix t` | Show clock |
| `prefix r` | Reload config (if bound) |

## Example `~/.tmux.conf`

```bash
# ── Prefix ────────────────────────────────────────────────────────────────────
# Remap prefix from Ctrl+b to Ctrl+a (easier to reach)
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# ── General ───────────────────────────────────────────────────────────────────
set -g default-terminal "screen-256color"   # 256-colour support
set -g history-limit 10000                  # Scrollback buffer size
set -g base-index 1                         # Start window numbering at 1
setw -g pane-base-index 1                   # Start pane numbering at 1
set -g escape-time 0                        # No delay for escape key
set -g display-time 2000                    # Status messages shown for 2s

# Reload config with prefix+r
bind r source-file ~/.tmux.conf \; display "Config reloaded"

# ── Mouse ─────────────────────────────────────────────────────────────────────
set -g mouse on                             # Enable mouse for pane/window select,
                                            # resize, and scrolling

# ── Scrolling ─────────────────────────────────────────────────────────────────
# Scroll with mouse wheel (enabled via mouse on above)
# Use vi keys in copy mode for manual scrolling
setw -g mode-keys vi
bind -n WheelUpPane   select-pane -t= \; copy-mode -e \; send-keys -M
bind -n WheelDownPane select-pane -t= \;                  send-keys -M

# ── Copy & Paste (vi-style) ───────────────────────────────────────────────────
bind prefix [ copy-mode                     # Enter copy mode
bind -T copy-mode-vi v   send -X begin-selection
bind -T copy-mode-vi y   send -X copy-selection-and-cancel
bind -T copy-mode-vi V   send -X select-line
bind -T copy-mode-vi C-v send -X rectangle-toggle  # Block selection

# Paste with prefix+p
bind p paste-buffer

# Copy to system clipboard (requires xclip on Linux or pbcopy on macOS)
# Linux:
bind -T copy-mode-vi y send -X copy-pipe-and-cancel "xclip -sel clip -i"
# macOS (comment out Linux line above and use this instead):
# bind -T copy-mode-vi y send -X copy-pipe-and-cancel "pbcopy"

# ── Pane Splitting ────────────────────────────────────────────────────────────
# More intuitive split keys (| and -)
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
unbind '"'
unbind %

# ── Pane Navigation ───────────────────────────────────────────────────────────
# Move between panes with Alt+arrow (no prefix needed)
bind -n M-Left  select-pane -L
bind -n M-Right select-pane -R
bind -n M-Up    select-pane -U
bind -n M-Down  select-pane -D
```
