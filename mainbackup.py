from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from extract_us_states import USStatesExtractor
# from extract_mexico_info import MexicoExtractor
# from login_wikipedia import WikipediaLogin

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

# Login to Wikipedia
# print("Logging into Wikipedia...")
# wikipedia_login = WikipediaLogin(driver)
# if wikipedia_login.login():
#     print("Login successful!")
    
    # Create an instance of USStatesExtractor and run the methods
    print("Extracting US states data...")
    us_extractor = USStatesExtractor(driver)
    us_extractor.navigate_to_us_states_page()
    us_extractor.extract_us_states_data()
    us_extractor.extract_etimologia()
    print("US states data extraction complete.")

    # Create an instance of MexicoExtractor and run the methods
    print("Extracting Mexico states data...")
    mexico_extractor = MexicoExtractor(driver)
    mexico_extractor.navigate_to_mexico_page()
    mexico_extractor.extract_mexico_data()
    print("Mexico states data extraction complete.")

    # Logout from Wikipedia
    print("Logging out of Wikipedia...")
    wikipedia_login.logout()
    print("Logout successful!")

# Close the browser
print("Closing the browser...")
driver.quit()
print("Browser closed.")
