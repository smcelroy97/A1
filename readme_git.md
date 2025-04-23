
1.  Fetch remote branches (origin/ou-grid, origin/ou-gridSM, ...) from github
    ```
    git fetch
    ```

2.  Commit your local changes and stash those changes you don't want to commit
    ```
    git checkout ou-gridSM
    git add <FILES TO COMMIT>
    git commit -m "<COMMIT TEXT>"
    git add .
    git stash 
    ```