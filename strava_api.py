import sys, os, json
from datetime import datetime, date
import time

import requests


# Load client secret from .env file
load_dotenv()
client_secret = os.getenv("CLIENT_SECRET")


# Check whether access token is valid or expired
def is_token_valid():
    with open("authentication_tokens.json", "r") as jsonFile:
        authentication_data = json.load(jsonFile)
        jsonFile.close
    # Update tokens if expired
    if authentication_data["expires_at"] < int(time.time()):
        refresh_token = get_token("refresh")
        request_access_and_refresh_tokens(refresh_token)


# Get either access or refresh token
def get_token(token_type):
    if token_type == "access":
        is_token_valid()
        with open("authentication_tokens.json", "r") as jsonFile:
            return json.load(jsonFile)["access_token"]
    elif token_type == "refresh":
        with open("authentication_tokens.json", "r") as jsonFile:
            return json.load(jsonFile)["refresh_token"]
    raise Exception("Please enter valid token type!")


# Output new access and refresh tokens to .json
def request_access_and_refresh_tokens(refresh_token):
    url = "https://www.strava.com/oauth/token"
    new_access_token_payload = {
        "client_id": 83375,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    r = requests.post(url, data=new_access_token_payload)
    with open("authentication_tokens.json", "w") as jsonFile:
        json.dump(r.json(), jsonFile)


# Request run certain from specific day using API
def fetch_run_from_strava(run_date):
    is_token_valid()
    access_token = get_token("access")
    run_date_epoch = int(datetime.strptime(run_date, "%d/%m/%Y").timestamp())
    url = "https://www.strava.com/api/v3/athlete/activities"
    # Create dictionary of parameters for the API request
    payload = {
        "before": run_date_epoch + 86400,  # 86400 seconds = 1 day
        "after": run_date_epoch,
        "page": 1,
        "per_page": 1,
    }
    headers = {"Authorization": "Bearer " + access_token}
    # Send request to API for activites
    return requests.get(url, params=payload, headers=headers)


# Output boolean value indicating whether run took place
def is_run_complete():
    # Get current date in format required by fetch_fun_from_strava
    current_date = date.today().strftime("%d/%m/%Y")
    # If run is complete on specified date, status code will = 200
    r = fetch_run_from_strava(current_date)
    # Evaluates to `True` if r.json() is not empty
    if r.json():
        return True
    return False
