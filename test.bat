@echo off

start cmd /c "cd server && set FLASK_APP=app.py && flask run"

cd update_client

pause

python test.py

cd ..