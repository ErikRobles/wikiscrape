import os
import re
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MexicoExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.output_directory = os.getcwd()

    def navigate_to_mexico_page(self):
        print("Opening Wikipedia page for 'Entidades federativas de México'...")
        self.driver.get('https://es.wikipedia.org/wiki/Anexo:Entidades_federativas_de_M%C3%A9xico')
        time.sleep(5)

    def extract_mexico_data(self):
        print("Extracting Mexico federative entities data...")
        try:
            tables = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'wikitable'))
            )
        except Exception as e:
            print(f"Error locating the tables: {e}")
            return

        if tables:
            print(f"Found {len(tables)} tables.")
            table_data = []
            headers = []

            # Extract data from the first table (Federative Entities by area, population, and density)
            first_table = tables[0]
            for header in first_table.find_elements(By.TAG_NAME, 'th'):
                headers.append(header.text.strip())
            print(f"Headers: {headers}")

            for row in first_table.find_elements(By.TAG_NAME, 'tr')[1:]:
                row_data = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, 'td')]
                if row_data:
                    table_data.append(row_data)
            print(f"Extracted {len(table_data)} rows.")

            df_federative_entities = pd.DataFrame(table_data, columns=headers)

            # Keep only the required columns and rename them appropriately
            required_columns = {
                'Nombre oficial': 'Official Name',
                'Superficie (km²)2': 'Area (km²)',
                'Población (1T2022)3': 'Population (2022)',
                'Densidad de población (hab/km²)': 'Population Density (hab/km²)'
            }
            df_federative_entities = df_federative_entities[list(required_columns.keys())]
            df_federative_entities.rename(columns=required_columns, inplace=True)

            # Initialize Excel writer
            output_file = os.path.join(self.output_directory, 'mexico_data.xlsx')
            print(f"Saving data to '{output_file}'...")

            with pd.ExcelWriter(output_file) as writer:
                df_federative_entities.to_excel(writer, sheet_name='Federative Entities', index=False)

                # Extract data from the second table (Historical Population of Mexico from Censuses)
                if len(tables) > 1:
                    second_table = tables[1]
                    table_data = []
                    headers = []

                    for header in second_table.find_elements(By.TAG_NAME, 'th'):
                        headers.append(header.text.strip())
                    print(f"Headers: {headers}")

                    for row in second_table.find_elements(By.TAG_NAME, 'tr')[1:]:
                        row_data = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, 'td')]
                        if row_data:
                            table_data.append(row_data)
                    print(f"Extracted {len(table_data)} rows.")

                    df_historical_population_censuses = pd.DataFrame(table_data, columns=headers)
                    df_historical_population_censuses.to_excel(writer, sheet_name='Historical Population Censuses', index=False)
                else:
                    print("Second table (Historical Population of Mexico from Censuses) not found.")

                # Extract data from the third table (Historical Population of Mexico from Population Projections)
                if len(tables) > 2:
                    third_table = tables[2]
                    table_data = []
                    headers = []

                    for header in third_table.find_elements(By.TAG_NAME, 'th'):
                        headers.append(header.text.strip())
                    print(f"Headers: {headers}")

                    for row in third_table.find_elements(By.TAG_NAME, 'tr')[1:]:
                        row_data = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, 'td')]
                        if row_data:
                            table_data.append(row_data)
                    print(f"Extracted {len(table_data)} rows.")

                    df_historical_population_projections = pd.DataFrame(table_data, columns=headers)
                    df_historical_population_projections.to_excel(writer, sheet_name='Historical Population Projections', index=False)
                else:
                    print("Third table (Historical Population of Mexico from Population Projections) not found.")

            print("Data saved successfully.")

            # Extract valid state links for toponymy
            state_links = []
            rows = first_table.find_elements(By.XPATH, './/tr')
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) > 0:
                    link = cells[0].find_element(By.TAG_NAME, 'a')
                    state_name = link.text.strip()
                    state_url = link.get_attribute('href')  # URL remains encoded

                    # Remove any <sup> elements from the state name
                    sup_elements = link.find_elements(By.XPATH, ".//sup")
                    for sup in sup_elements:
                        self.driver.execute_script("arguments[0].remove();", sup)

                    state_name = link.text.strip()  # Re-fetch the state name after removing <sup> elements
                    
                    # Ensure only valid state names are processed
                    if state_name and state_url and state_name not in ["nota", "", None]:
                        state_links.append((state_name, state_url))
                        print(f"Extracted link: State: {state_name}, URL: {state_url}")
            print(f"Extracted {len(state_links)} state links.")

            self.extract_toponimia(state_links)

    def extract_toponimia(self, state_links):
        toponimia_data = []

        for state_name, state_url in state_links:
            print(f"Extracting 'Toponimia' for {state_name}...")
            self.driver.get(state_url)
            time.sleep(5)

            try:
                xpaths = [
                    "//span[@id='Toponimia']/following::p[1]",
                    "//span[contains(@id, 'Toponimia')]/following::p[1]",
                    "//span[contains(text(), 'Toponimia')]/following::p[1]",
                    "//span[contains(text(), 'Toponimia y gentilicio')]/following::p[1]",
                    "//h2[span[@id='Toponimia']]/following-sibling::p[1]",
                    "//h2[span[contains(@id, 'Toponimia')]]/following-sibling::p[1]",
                    "//h2[span[contains(text(), 'Toponimia')]]/following-sibling::p[1]",
                    "//h2[span[contains(text(), 'Toponimia y gentilicio')]]/following-sibling::p[1]",
                    "//h3[span[@id='Toponimia']]/following-sibling::p[1]",
                    "//h3[span[contains(@id, 'Toponimia')]]/following-sibling::p[1]",
                    "//h3[span[contains(text(), 'Toponimia')]]/following-sibling::p[1]",
                    "//h3[span[contains(text(), 'Toponimia y gentilicio')]]/following-sibling::p[1]",
                    "//h4[span[@id='Toponimia']]/following-sibling::p[1]",
                    "//h4[span[contains(@id, 'Toponimia')]]/following-sibling::p[1]",
                    "//h4[span[contains(text(), 'Toponimia')]]/following-sibling::p[1]",
                    "//h4[span[contains(text(), 'Toponimia y gentilicio')]]/following-sibling::p[1]",
                    "//p[contains(., 'Toponimia')]"
                ]
                
                toponimia_text = None
                for xpath in xpaths:
                    try:
                        toponimia_section = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        toponimia_text = toponimia_section.text.strip()
                        if toponimia_text:
                            break
                    except:
                        continue

                if toponimia_text and 'municipios' not in toponimia_text:
                    toponimia_data.append([state_name, toponimia_text])
                    print(f"Extracted 'Toponimia' for {state_name}.")
                else:
                    print(f"'Toponimia' section not found or incorrect for {state_name}.")
                    toponimia_data.append([state_name, ""])
            except Exception as e:
                print(f"Failed to extract 'Toponimia' for {state_name}: {e}")
                toponimia_data.append([state_name, ""])
                continue

        df_toponimia = pd.DataFrame(toponimia_data, columns=["State", "Toponimia"])
        
        # Filter out invalid entries
        df_toponimia = df_toponimia[df_toponimia['State'].apply(lambda x: x not in ["nota", "", None])]
        df_toponimia = df_toponimia.drop_duplicates(subset=["State"])
        
        output_file_toponimia = os.path.join(self.output_directory, 'mexico_toponimia.xlsx')
        print(f"Saving 'Toponimia' data to '{output_file_toponimia}'...")
        df_toponimia.to_excel(output_file_toponimia, index=False)
        print("Toponimia data saved successfully.")