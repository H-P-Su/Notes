# Vim Shortcuts

## Modes

| Key | Action |
|-----|--------|
| `Esc` | Normal mode |
| `i` | Insert before cursor |
| `a` | Insert after cursor |
| `I` | Insert at start of line |
| `A` | Insert at end of line |
| `o` | New line below, insert |
| `O` | New line above, insert |
| `v` | Visual mode |
| `V` | Visual line mode |
| `Ctrl+v` | Visual block mode |
| `:` | Command mode |

## Navigation

| Key | Action |
|-----|--------|
| `h j k l` | Left / Down / Up / Right |
| `w` | Next word start |
| `b` | Previous word start |
| `e` | Next word end |
| `0` | Start of line |
| `^` | First non-blank character |
| `$` | End of line |
| `gg` | Top of file |
| `G` | Bottom of file |
| `{n}G` | Go to line n |
| `Ctrl+d` | Half page down |
| `Ctrl+u` | Half page up |
| `Ctrl+f` | Full page down |
| `Ctrl+b` | Full page up |
| `%` | Jump to matching bracket |

## Editing

| Key | Action |
|-----|--------|
| `x` | Delete character |
| `dd` | Delete line |
| `d{motion}` | Delete by motion (e.g. `dw`, `d$`) |
| `cc` | Change line |
| `c{motion}` | Change by motion |
| `yy` | Yank (copy) line |
| `y{motion}` | Yank by motion |
| `p` | Paste after cursor |
| `P` | Paste before cursor |
| `u` | Undo |
| `Ctrl+r` | Redo |
| `r{c}` | Replace character with c |
| `~` | Toggle case |
| `.` | Repeat last change |
| `J` | Join line below |
| `>>` | Indent line |
| `<<` | Dedent line |

## Search & Replace

| Key | Action |
|-----|--------|
| `/{pattern}` | Search forward |
| `?{pattern}` | Search backward |
| `n` | Next match |
| `N` | Previous match |
| `*` | Search word under cursor (forward) |
| `#` | Search word under cursor (backward) |
| `:%s/old/new/g` | Replace all in file |
| `:%s/old/new/gc` | Replace all with confirmation |
| `:s/old/new/g` | Replace all on current line |

## Files & Buffers

| Key | Action |
|-----|--------|
| `:w` | Save |
| `:w {file}` | Save as |
| `:q` | Quit |
| `:q!` | Quit without saving |
| `:wq` / `ZZ` | Save and quit |
| `:e {file}` | Open file |
| `:bn` | Next buffer |
| `:bp` | Previous buffer |
| `:bd` | Close buffer |
| `:ls` | List buffers |

## Windows & Tabs

| Key | Action |
|-----|--------|
| `:sp` | Horizontal split |
| `:vsp` | Vertical split |
| `Ctrl+w h/j/k/l` | Move between windows |
| `Ctrl+w =` | Equalize window sizes |
| `Ctrl+w q` | Close window |
| `:tabnew` | New tab |
| `gt` | Next tab |
| `gT` | Previous tab |

## Marks & Jumps

| Key | Action |
|-----|--------|
| `m{a-z}` | Set mark |
| `` `{a-z} `` | Jump to mark |
| `Ctrl+o` | Jump back |
| `Ctrl+i` | Jump forward |
| `gi` | Return to last insert position |

## Macros

| Key | Action |
|-----|--------|
| `q{a-z}` | Start recording macro |
| `q` | Stop recording |
| `@{a-z}` | Play macro |
| `@@` | Replay last macro |
| `{n}@{a-z}` | Play macro n times |

## Text Objects (use with `d`, `c`, `y`, `v`)

| Key | Action |
|-----|--------|
| `iw` / `aw` | Inner / around word |
| `is` / `as` | Inner / around sentence |
| `ip` / `ap` | Inner / around paragraph |
| `i"` / `a"` | Inner / around double quotes |
| `i'` / `a'` | Inner / around single quotes |
| `i)` / `a)` | Inner / around parentheses |
| `i]` / `a]` | Inner / around brackets |
| `i}` / `a}` | Inner / around braces |
| `it` / `at` | Inner / around HTML tag |
