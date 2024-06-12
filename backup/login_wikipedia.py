from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Replace these with your Wikipedia username and password
WIKIPEDIA_USERNAME = os.getenv('WIKIPEDIA_USERNAME')
WIKIPEDIA_PASSWORD = os.getenv('WIKIPEDIA_PASSWORD')

# Initialize Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Initialize the Chrome driver using ChromeDriverManager
print("Setting up Chrome driver...")
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open Wikipedia login page
print("Opening Wikipedia login page...")
driver.get('https://en.wikipedia.org/w/index.php?title=Special:UserLogin&returnto=Main+Page')

# Add a sleep to see the page load
time.sleep(5)

# Enter username
print("Entering username...")
username_input = driver.find_element(By.ID, 'wpName1')
username_input.send_keys(WIKIPEDIA_USERNAME)

# Enter password
print("Entering password...")
password_input = driver.find_element(By.ID, 'wpPassword1')
password_input.send_keys(WIKIPEDIA_PASSWORD)

# Submit the login form
print("Submitting the login form...")
login_button = driver.find_element(By.ID, 'wpLoginAttempt')
login_button.click()

# Wait for the user menu to appear and interact with it
try:
    user_menu = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'pt-userpage'))
    )
    print("Login successful!")

    # Move to the user menu to reveal the logout option
    print("Revealing logout option...")
    driver.execute_script("arguments[0].click();", user_menu)
    time.sleep(2)  # Wait a moment for the menu to open

    # Wait for the logout link to be clickable and click it
    print("Logging out...")
    logout_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'pt-logout'))
    )
    driver.execute_script("arguments[0].click();", logout_link)

    # Add a sleep to ensure logout completes
    time.sleep(5)
    print("Logout successful!")
except Exception as e:
    print("Login failed or logout link not found:", e)

# Close the browser
print("Closing the browser...")
driver.quit()
print("Browser closed.")