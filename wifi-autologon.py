import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser
from plyer import notification

# Load credentials from system-wide config file
CONFIG_PATH = "/etc/wifi-login.conf"

if not os.path.exists(CONFIG_PATH):
    print("[ERROR] Config file not found: /etc/wifi-login.conf")
    exit(1)

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

USERNAME = config.get("DEFAULT", "WIFI_USERNAME", fallback=None)
PASSWORD = config.get("DEFAULT", "WIFI_PASSWORD", fallback=None)

if not USERNAME or not PASSWORD:
    print("[ERROR] Missing credentials in /etc/wifi-login.conf")
    exit(1)

# Check if the internet is accessible
TEST_URL = "http://connectivity-check.ubuntu.com/"
CAPTIVE_PORTAL_KEYWORDS = ["login", "captive", "portal", "sign", "auth"]

try:
    response = requests.get(TEST_URL, allow_redirects=True, timeout=5)
    
    # Check if redirected to a captive portal
    if response.url != TEST_URL:  # We got redirected!
        print(f"[INFO] Redirected to {response.url}, captive portal detected.")
    elif any(keyword in response.text.lower() for keyword in CAPTIVE_PORTAL_KEYWORDS):
        print("[INFO] Captive portal detected based on page content.")
    else:
        print("[INFO] Internet access is working, no need to log in.")
        exit(0)

except requests.RequestException as e:
    print(f"[ERROR] Network check failed: {e}")

print("[INFO] Proceeding with login...")

# Configure Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Remove this line to debug
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("[INFO] Navigating to captive portal...")
    driver.get(TEST_URL)
    
    # Wait for redirection
    WebDriverWait(driver, 10).until(EC.url_contains("portal"))
    
    # Fill in username
    print("[INFO] Entering username...")
    username_field = driver.find_element(By.ID, "user.username")
    username_field.clear()
    username_field.send_keys(USERNAME)

    # Fill in password
    print("[INFO] Entering password...")
    password_field = driver.find_element(By.ID, "user.password")
    password_field.clear()
    password_field.send_keys(PASSWORD)

    # Accept terms
    print("[INFO] Accepting terms...")
    checkbox = driver.find_element(By.ID, "aupAccepted")
    ActionChains(driver).move_to_element(checkbox).click().perform()

    # Click login button
    print("[INFO] Clicking login button...")
    login_button = driver.find_element(By.ID, "ui_login_signon_button")
    login_button.click()

    # Wait for successful login
    time.sleep(5)

    print("[SUCCESS] Login successful!")
    notification.notify(
        title="WiFi Auto-Login",
        message="Successfully logged into Tk-gjestenett!",
        timeout=5
    )

except Exception as e:
    print(f"[ERROR] Login failed: {e}")
finally:
    print("[INFO] Closing browser...")
    driver.quit()

