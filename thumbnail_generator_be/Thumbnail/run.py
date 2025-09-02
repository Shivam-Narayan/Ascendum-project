import os


commands = [
    "pip install -r requirements_server.txt",
]

for command in commands:
    os.system(command)