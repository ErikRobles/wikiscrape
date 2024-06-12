from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Initialize the Chrome driver using ChromeDriverManager
print("Setting up Chrome driver...")
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open Wikipedia
print("Opening Wikipedia...")
driver.get('https://www.wikipedia.org/')

# Add a sleep to see the page load
time.sleep(5)

# Find the search input and search for "Python (programming language)"
print("Finding the search input...")
search_input = driver.find_element(By.NAME, 'search')
print("Entering search term...")
search_input.send_keys('Python (programming language)')
search_input.send_keys(Keys.RETURN)

# Add a sleep to see the search result
time.sleep(5)

# Wait for a few seconds and then close the browser
print("Closing the browser...")
driver.quit()
print("Browser closed.")
