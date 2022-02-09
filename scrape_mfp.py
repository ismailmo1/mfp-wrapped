import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
# login to myfitness pal
session = requests.session()

# grab csrf token
res = session.get("https://www.myfitnesspal.com/api/auth/csrf")
csrf_token = json.loads(res.text)["csrfToken"]

res = session.post(
    "https://www.myfitnesspal.com/api/auth/callback/credentials?",
    data={
        "username": os.getenv("MFP_USER"),
        "password": os.getenv("MFP_PASS"),
        "csrfToken": csrf_token,
        "callbackUrl": "https://www.myfitnesspal.com/account/login?callbackUrl=https%3A%2F%2F\
            www.myfitnesspal.com%2Ffood%2Fdiary",
    },
)

print(res.text.find("Incorrect username"))
