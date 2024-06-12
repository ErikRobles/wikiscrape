import os
import re
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class USStatesExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.output_directory = os.getcwd()

    def navigate_to_us_states_page(self):
        print("Opening Wikipedia page for 'Estados de los Estados Unidos'...")
        self.driver.get('https://es.wikipedia.org/wiki/Estado_de_los_Estados_Unidos')
        time.sleep(5)

    def extract_us_states_data(self):
        print("Extracting list of US states...")
        try:
            # Locate the table containing the list of states
            table = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//table[contains(@class,"wikitable")][1]'))
            )
        except Exception as e:
            print(f"Error locating the table: {e}")
            return None

        if table:
            print("Found the table.")
            state_data = []
            headers = table.find_elements(By.TAG_NAME, 'th')
            state_index = None

            # Find the column index with header "Estado"
            for index, header in enumerate(headers):
                if header.text.strip() == "Estado":
                    state_index = index
                    break

            if state_index is None:
                print("Could not find the 'Estado' header.")
                return None

            rows = table.find_elements(By.TAG_NAME, 'tr')
            print(f"Found {len(rows)} rows in the table.")

            for row in rows[1:]:  # Skip header row
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) > state_index:
                    state_element = cells[state_index].find_element(By.TAG_NAME, 'a')
                    state_name = state_element.text.strip()
                    state_url = state_element.get_attribute('href')
                    
                    # Remove any <sup> elements from the state name
                    sup_elements = cells[state_index].find_elements(By.TAG_NAME, 'sup')
                    for sup in sup_elements:
                        self.driver.execute_script("arguments[0].remove();", sup)
                    
                    state_name = state_element.text.strip()  # Re-fetch the state name after removing <sup> elements
                    state_data.append([state_name, state_url])
                    print(f"Added state: {state_name}")

            print(f"Extracted {len(state_data)} states.")

            # Create DataFrame
            df_us_states = pd.DataFrame(state_data, columns=["State", "URL"])
            return df_us_states

    def extract_etimologia(self, df_us_states):
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
        return df_etimologia

    def save_to_excel(self, df_us_states, df_etimologia):
        with pd.ExcelWriter(os.path.join(self.output_directory, 'us_states.xlsx')) as writer:
            df_us_states.to_excel(writer, sheet_name='States', index=False)
            df_etimologia.to_excel(writer, sheet_name='Etimología', index=False)
        print("US states data saved successfully to 'us_states.xlsx'.")

