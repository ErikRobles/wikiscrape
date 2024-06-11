from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
import re

# List of the 32 Mexican states
mexican_states = [
    "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
    "Chiapas", "Chihuahua", "Ciudad de México", "Coahuila de Zaragoza",
    "Colima", "Durango", "Guanajuato", "Guerrero", "Hidalgo", "Jalisco",
    "Estado de México", "Michoacán de Ocampo", "Morelos", "Nayarit",
    "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo",
    "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas",
    "Tlaxcala", "Veracruz de Ignacio de la Llave", "Yucatán", "Zacatecas"
]

# Define the directory where you want to save the files
output_directory = os.getcwd()  # This uses the current working directory
# Alternatively, specify a different directory like below
# output_directory = '/path/to/your/directory'

# Create the directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Define file paths
output_file = os.path.join(output_directory, 'mexico_federative_entities.xlsx')
output_file_toponimia = os.path.join(output_directory, 'mexico_toponimia.xlsx')

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

# Open the Wikipedia page
print("Opening Wikipedia page for 'Entidades federativas de México'...")
driver.get('https://es.wikipedia.org/wiki/Anexo:Entidades_federativas_de_M%C3%A9xico')

# Add a sleep to see the page load
time.sleep(5)

# Extract table data
print("Extracting table data...")
tables = WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'wikitable'))
)

# Check if tables were found
if tables:
    print(f"Found {len(tables)} tables.")
    # Extract the table data into a DataFrame
    table_data = []
    headers = []

    # We are targeting the first table on the page
    first_table = tables[0]
    
    # Extract headers
    for header in first_table.find_elements(By.TAG_NAME, 'th'):
        headers.append(header.text.strip())
    print(f"Headers: {headers}")

    # Extract rows
    for row in first_table.find_elements(By.TAG_NAME, 'tr')[1:]:
        row_data = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, 'td')]
        if row_data:
            table_data.append(row_data)
    print(f"Extracted {len(table_data)} rows.")

    # Create DataFrame
    df = pd.DataFrame(table_data, columns=headers)

    # Replace numbers in 'Ciudad más poblada' with the corresponding capital names
    for i, row in df.iterrows():
        ciudad_mas_poblada = row['Ciudad más poblada']
        capital = row['Capital']
        if re.match(r"^\d", ciudad_mas_poblada):
            df.at[i, 'Ciudad más poblada'] = capital

    # Correct handling of "Iztapalapa" superscript
    df['Ciudad más poblada'] = df['Ciudad más poblada'].apply(lambda x: re.sub(r'nota \d+', '', x))

    # Save the data to an Excel file
    print(f"Saving data to '{output_file}'...")
    df.to_excel(output_file, index=False)
    print("Data saved successfully.")

    # Extract valid state links
    state_links = []
    unique_states = set()
    links = first_table.find_elements(By.XPATH, './/tr//td//a')
    for link in links:
        state_name = link.text.strip()
        state_url = link.get_attribute('href')
        # Filter out empty, duplicate, irrelevant, and non-state links
        if state_name in mexican_states and state_name not in unique_states:
            state_links.append((state_name, state_url))
            unique_states.add(state_name)
    print(f"Extracted {len(state_links)} state links.")

    # Extract "Toponimia" for each state
    toponimia_data = []

    for state_name, state_url in state_links:
        print(f"Extracting 'Toponimia' for {state_name}...")
        driver.get(state_url)
        time.sleep(5)  # Wait for the page to load

        try:
            # Define potential XPaths for the "Toponimia" section
            xpaths = [
                "//span[@id='Toponimia']/following::p[1]",
                "//h2[span[@id='Toponimia']]/following-sibling::p[1]",
                "//h3[span[@id='Toponimia']]/following-sibling::p[1]",
                "//h4[span[@id='Toponimia']]/following-sibling::p[1]"
            ]
            
            toponimia_text = None
            for xpath in xpaths:
                try:
                    toponimia_section = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    toponimia_text = toponimia_section.text.strip()
                    break
                except:
                    continue

            if toponimia_text:
                toponimia_data.append([state_name, toponimia_text])
                print(f"Extracted 'Toponimia' for {state_name}.")
            else:
                print(f"'Toponimia' section not found for {state_name}.")
                toponimia_data.append([state_name, ""])
        except Exception as e:
            print(f"Failed to extract 'Toponimia' for {state_name}: {e}")
            toponimia_data.append([state_name, ""])
            continue  # Skip to the next state

    # Create DataFrame for Toponimia
    df_toponimia = pd.DataFrame(toponimia_data, columns=["State", "Toponimia"])

    # Save the Toponimia data to an Excel file
    print(f"Saving 'Toponimia' data to '{output_file_toponimia}'...")
    df_toponimia.to_excel(output_file_toponimia, index=False)
    print("Toponimia data saved successfully.")

# Close the browser
print("Closing the browser...")
driver.quit()
print("Browser closed.")
