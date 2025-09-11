import os


commands = [
    "pip install -r requirements.txt",
    "python manage.py makemigrations chatbot",
    "python manage.py migrate",
    "python manage.py runserver",
]

for command in commands:
    os.system(command)