# Git Basics

[tutorial](https://www.youtube.com/watch?v=HVsySz-h9r4&t=4s)

- `git remote -v` shows the remote repository
- `git branch -a` shows the branches
- `git branch --merged`  shows which branhces were merged into the actual branch
- `git log` shows all the commits on the current branch

## Configuration

- `git config --global user.name "woka"` sets the user
- `git config -- global user.email "w.kloos@gmx.de"` sets the user email, used for accessing repository
- `git config --list`: shows the configuration

## Setup git repository

### local code base to start tracking in git

1. go to the folder where the project is located and
2. `git init` makes git repository from the folder
3. `git status` to show untracked files in the folder
4. create `.gitignore` file (test file)
5. rerun `git status` to check if unwanted files are ignored
6. `git add .` or `git add -A` to add all files to stage
    - `git add file.extension` to add one file to stage
7. `git reset` to remove all files from stage or `git reset file.extension` to remove one file from the stage
8. `git commit -m "message"` to commit the files from the stage are to repository

### clone repository from remote repository

1. `git clone <url> <where to clone>`
    - `.` to clone to current directory
2. `git remote -v` lists information about the repository
3. `git branch -a` shows all the branches including branches on remote repository
4. after chenges on the code `git diff` to show the changes, which were done. Works only if the file is already tracked
5. `git add -A` to add changes to the stage
6. `git commit -m "message` to commit on local repository
7. ! `git pull origin master` to pull first the changes from the remote repository to the local, where master is the branch
8. `git push origin master` to push the changes to remote repository

### branching

1. `git branch <branch-name>` to create a branch
2. `git checkout <branch-name>` to change to the branch
3. add changes as described above to the branche
4. `git push -u origin <branch-name>` to push the branch to remote repository

> to add automatically the branch to remote repository - can be done instead

```text
git pull
git push
```

1. `git checkout master` to change to the local master branch
2. `git pull origine master` to update master
3. `git branch --merged` shows the branches which were merged
4. `git merge <branch-name>` to merge the branch to the master branch -> master branch can be pushed like before (with `pull` nd `push` to remote
5. `git branch -d <branch-name>` to delete the branch from local repository
6. `git push origin --delete <branch-name>` to delete the branch from remote repository
