from flask import Flask, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import threading
import time
import os

app = Flask(__name__)

token_data = {
    "access_token": None,
    "status": "Not started"
}

def run_selenium_oauth():
    global token_data
    APP_ID = "YOUR_APP_ID"  # Replace with your Facebook App ID
    REDIRECT_URI = "https://www.facebook.com/connect/login_success.html"
    SCOPES = "email,public_profile"
    oauth_url = (
        f"https://www.facebook.com/v19.0/dialog/oauth?"
        f"client_id={APP_ID}&redirect_uri={REDIRECT_URI}"
        f"&response_type=token&scope={SCOPES}"
    )

    options = Options()
    options.binary_location = "/usr/bin/chromium"  # Location in Docker/Render
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=options)

    try:
        token_data["status"] = "Browser opened, loading login page..."
        driver.get(oauth_url)

        max_wait = 60  # seconds
        for _ in range(max_wait):
            url = driver.current_url
            if "access_token=" in url:
                token_part = url.split("access_token=")[1]
                access_token = token_part.split("&")[0]
                token_data["access_token"] = access_token
                token_data["status"] = "Token retrieved"
                break
            time.sleep(1)
        else:
            token_data["status"] = "Timeout: Token not found"
    except Exception as e:
        token_data["status"] = f"Error: {str(e)}"
    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_oauth')
def start_oauth():
    token_data["access_token"] = None
    token_data["status"] = "Starting OAuth..."
    thread = threading.Thread(target=run_selenium_oauth)
    thread.start()
    return jsonify({"status": "OAuth process started"})

@app.route('/token_status')
def token_status():
    return jsonify(token_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Get port from env, default 5000
    app.run(host='0.0.0.0', port=port)
