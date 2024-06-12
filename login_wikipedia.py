import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WikipediaLogin:
    def __init__(self, driver):
        self.driver = driver
        self.username = os.getenv('WIKIPEDIA_USERNAME')
        self.password = os.getenv('WIKIPEDIA_PASSWORD')

    def login(self):
        if not self.username or not self.password:
            print("Wikipedia credentials are not set in environment variables.")
            return False

        print("Opening Wikipedia login page...")
        self.driver.get('https://en.wikipedia.org/w/index.php?title=Special:UserLogin&returnto=Main+Page')

        # Add a sleep to see the page load
        time.sleep(5)

        # Enter username
        print("Entering username...")
        username_input = self.driver.find_element(By.ID, 'wpName1')
        username_input.send_keys(self.username)

        # Enter password
        print("Entering password...")
        password_input = self.driver.find_element(By.ID, 'wpPassword1')
        password_input.send_keys(self.password)

        # Submit the login form
        print("Submitting the login form...")
        login_button = self.driver.find_element(By.ID, 'wpLoginAttempt')
        login_button.click()

        # Wait for the user menu to appear and interact with it
        try:
            user_menu = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, 'pt-userpage'))
            )
            print("Login successful!")
            return True
        except Exception as e:
            print("Login failed:", e)
            return False

    def logout(self):
        try:
            # Move to the user menu to reveal the logout option
            print("Revealing logout option...")
            user_menu = self.driver.find_element(By.ID, 'pt-userpage')
            self.driver.execute_script("arguments[0].click();", user_menu)
            time.sleep(2)  # Wait a moment for the menu to open

            # Wait for the logout link to be clickable and click it
            print("Logging out...")
            logout_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'pt-logout'))
            )
            self.driver.execute_script("arguments[0].click();", logout_link)

            # Add a sleep to ensure logout completes
            time.sleep(5)
            print("Logout successful!")
        except Exception as e:
            print("Logout failed or logout link not found:", e)
