import os
from dotenv import load_dotenv
import subprocess

subprocess.run(["pip", "freeze"], stdout=open("req.txt", "w"))

packages = []
with open("req.txt", "r") as file:
    for line in file:
        packages.append(line.split("==")[0])

with open("req.txt", "w") as file:
    file.write("\n".join(packages))

load_dotenv()
print(os.getenv("POSTGRES_DB"))
print(os.getenv("GOOGLE_OAUTH_CLIENT_ID"))


# initial db scheme inside container
