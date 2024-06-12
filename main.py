from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from extract_mexico_info import MexicoExtractor

# Add debugging statements
print("Starting script...")

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

# Create an instance of MexicoExtractor and run the methods
print("Extracting Mexico states data...")
mexico_extractor = MexicoExtractor(driver)
mexico_extractor.navigate_to_mexico_page()
mexico_extractor.extract_mexico_data()
print("Mexico states data extraction complete.")

# Close the browser
print("Closing the browser...")
driver.quit()
print("Browser closed.")
