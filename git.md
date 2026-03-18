# Git Common Commands

## Setup

| Command | Action |
|---------|--------|
| `git config --global user.name "Name"` | Set username |
| `git config --global user.email "email"` | Set email |
| `git config --list` | Show config |

## Starting a Repo

| Command | Action |
|---------|--------|
| `git init` | Init a new repo |
| `git clone <url>` | Clone a remote repo |

## Staging & Committing

| Command | Action |
|---------|--------|
| `git status` | Show working tree status |
| `git add <file>` | Stage a file |
| `git add .` | Stage all changes |
| `git commit -m "message"` | Commit staged changes |
| `git commit --amend` | Edit last commit |
| `git diff` | Show unstaged changes |
| `git diff --staged` | Show staged changes |

## Branches

| Command | Action |
|---------|--------|
| `git branch` | List branches |
| `git branch <name>` | Create a branch |
| `git switch <name>` | Switch to a branch |
| `git switch -c <name>` | Create and switch |
| `git merge <name>` | Merge branch into current |
| `git rebase <name>` | Rebase onto branch |
| `git branch -d <name>` | Delete branch |

## Remote

| Command | Action |
|---------|--------|
| `git remote -v` | List remotes |
| `git remote add origin <url>` | Add a remote |
| `git fetch origin` | Fetch without merging |
| `git pull origin <branch>` | Fetch and merge |
| `git push -u origin <branch>` | Push and set upstream |

## Log & History

| Command | Action |
|---------|--------|
| `git log` | Full commit log |
| `git log --oneline` | Compact log |
| `git log --oneline --graph` | Log with branch graph |
| `git show <commit>` | Show a commit's changes |
| `git blame <file>` | Show who changed each line |

## Undoing

| Command | Action |
|---------|--------|
| `git restore <file>` | Discard unstaged changes |
| `git restore --staged <file>` | Unstage a file |
| `git revert <commit>` | New commit that undoes a commit |
| `git reset --soft HEAD~1` | Undo last commit, keep staged |
| `git reset --hard HEAD~1` | Undo last commit, discard changes |

## Stash

| Command | Action |
|---------|--------|
| `git stash` | Stash uncommitted changes |
| `git stash pop` | Apply and drop latest stash |
| `git stash list` | List stashes |
| `git stash drop` | Discard latest stash |

## Tags

| Command | Action |
|---------|--------|
| `git tag v1.0` | Create a lightweight tag |
| `git tag -a v1.0 -m "msg"` | Create an annotated tag |
| `git push origin --tags` | Push all tags |
