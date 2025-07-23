@echo off
echo WARNING: This will reset all local changes and pull from remote!
echo.
echo Proceeding with git reset --hard...
git reset --hard
echo Pulling from remote...
git pull
echo Done!