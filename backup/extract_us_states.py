import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class USStatesExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.output_directory = os.getcwd()
        self.us_states = [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
            "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
            "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", 
            "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", 
            "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
            "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", 
            "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
        ]

    def navigate_to_us_states_page(self):
        print("Opening Wikipedia page for 'Estados de los Estados Unidos'...")
        self.driver.get('https://es.wikipedia.org/wiki/Estado_de_los_Estados_Unidos')
        time.sleep(5)

    def extract_us_states_data(self):
        print("Extracting list of US states...")
        try:
            # Locate the list of states by finding all links in the main content
            states_elements = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//table[contains(@class,"wikitable")][1]//a'))
            )
        except Exception as e:
            print(f"Error: {e}")
            return

        if states_elements:
            print(f"Found {len(states_elements)} state elements.")
            state_data = []

            for element in states_elements:
                state_name = element.text.strip()
                state_url = element.get_attribute('href')
                # Check if the URL points to a state page and if the state is in our predefined list
                if state_url and "/wiki/" in state_url and state_name in self.us_states:
                    state_data.append([state_name, state_url])
            print(f"Extracted {len(state_data)} states.")

            # Create DataFrame
            df_us_states = pd.DataFrame(state_data, columns=["State", "URL"])
            output_file_us_states = os.path.join(self.output_directory, 'us_states.xlsx')
            print(f"Saving data to '{output_file_us_states}'...")
            df_us_states.to_excel(output_file_us_states, index=False)
            print("Data saved successfully.")

    def extract_etimologia(self):
        # Load the Excel file containing the list of US states
        df_us_states = pd.read_excel(os.path.join(self.output_directory, 'us_states.xlsx'))
        state_links_us = []

        for index, row in df_us_states.iterrows():
            state_name = row['State']
            state_url = row['URL']
            if state_name and state_url:
                state_links_us.append((state_name, state_url))
        print(f"Extracted {len(state_links_us)} state links.")

        etimologia_data = []

        for state_name, state_url in state_links_us:
            print(f"Extracting 'Etimología' for {state_name}...")
            self.driver.get(state_url)
            time.sleep(5)

            try:
                xpaths = [
                    "//span[@id='Etimología']/following::p[1]",
                    "//span[@id='Etimología']/following::p",
                    "//h2[span[@id='Etimología']]/following-sibling::p[1]",
                    "//h3[span[@id='Etimología']]/following-sibling::p[1]",
                    "//h4[span[@id='Etimología']]/following-sibling::p[1]"
                ]
                
                etimologia_text = None
                for xpath in xpaths:
                    try:
                        etimologia_section = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        etimologia_text = etimologia_section.text.strip()
                        if etimologia_text:
                            break
                    except:
                        continue

                if etimologia_text:
                    etimologia_data.append([state_name, etimologia_text])
                    print(f"Extracted 'Etimología' for {state_name}.")
                else:
                    print(f"'Etimología' section not found for {state_name}.")
                    etimologia_data.append([state_name, ""])
            except Exception as e:
                print(f"Failed to extract 'Etimología' for {state_name}: {e}")
                etimologia_data.append([state_name, ""])
                continue

        df_etimologia = pd.DataFrame(etimologia_data, columns=["State", "Etimología"])
        output_file_etimologia = os.path.join(self.output_directory, 'us_states_etimologia.xlsx')
        print(f"Saving 'Etimología' data to '{output_file_etimologia}'...")
        df_etimologia.to_excel(output_file_etimologia, index=False)
        print("Etimología data saved successfully.")

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

# Create an instance of USStatesExtractor and run the methods
us_extractor = USStatesExtractor(driver)
us_extractor.navigate_to_us_states_page()
us_extractor.extract_us_states_data()
us_extractor.extract_etimologia()

# Close the browser
print("Closing the browser...")
driver.quit()
print("Browser closed.")
