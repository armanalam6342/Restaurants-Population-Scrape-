#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries and modules
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc 
from selenium import webdriver
import pandas as pd
import time
from bs4 import BeautifulSoup
from datetime import date
import re
import warnings

# Ignore warnings
warnings.filterwarnings('ignore')

# Initialize the Chrome WebDriver
driver = uc.Chrome()

# Navigate to the webpage containing the list of districts in India
driver.get("https://simple.wikipedia.org/wiki/List_of_districts_of_India")

# Create a list to store state names
state = []

# Extract state names from the webpage
for j in driver.find_elements(By.XPATH, "//h3//span[@class='mw-headline']"):
    state.append(j.text)

# Find the tables containing district information on the webpage
table = driver.find_elements(By.XPATH, "//table[@class = 'wikitable sortable jquery-tablesorter']")

# Create a list to store data from the tables
z = []

# Iterate through the tables and rows to extract district information
for t in range(len(table)):
    for j in table[t].find_elements(By.TAG_NAME, "tr"):
        b = []
        for k in j.find_elements(By.TAG_NAME, "td"):
            b.append(k.text)
        b.append(state[t])
        z.append(b)

# Filter out empty sublists from the list
final_list = [sublist for sublist in z if len(sublist) > 1]

# Create a DataFrame with the district population data
population = pd.DataFrame(final_list).iloc[:, 2:8]
population.columns = ["District", "Headquarter", "Population", "Area", "Density", "state"]

# Save the population data to a CSV file
population.to_csv("population.csv", index=False)

# Create an empty DataFrame for restaurant data
df = pd.DataFrame(columns=["name", "rate", "ratings", "address", "district"], index=range(1000000))

# Read the population data from the CSV file
population = pd.read_csv("population.csv")

# Initialize an index for iterating through restaurant data
index = 0

# Iterate through the districts and search for restaurants in each district
for dis in population["District"]:
    print("Started District", dis)
    url = f"https://www.google.com/search?tbs=lf:1,lf_ui:9&tbm=lcl&sxsrf=AB5stBhAO8lbUt5izC4b5_hILNHB7pSCMg:1688821960423&q=restaurants+in+{dis}"
    driver.get(url)
    time.sleep(3)
    
    # Iterate through multiple pages of search results
    for k in range(30):
        for i in driver.find_elements(By.XPATH, "//a[@class='vwVdIc wzN8Ac rllt__link a-no-hover-decoration']"):
            try:
                # Click on a restaurant link
                try:
                    i.click()
                except:
                    time.sleep(2)
                    i.click()
                time.sleep(2)
                try:
                    # Extract restaurant rating
                    df["rate"][index] = (i.find_element(By.XPATH, ".//span[@class='yi40Hd YrbPuc']").text)
                except:
                    pass
                try:
                    # Extract restaurant ratings
                    df["ratings"][index] = (i.find_element(By.XPATH, ".//span[@class='RDApEe YrbPuc']").text)
                except:
                    pass
                try:
                    # Extract restaurant name
                    df["name"][index] = (driver.find_element(By.XPATH, "//div[@class = 'SPZz6b']").text)
                except:
                    pass
                try:
                    # Extract restaurant address
                    df["address"][index] = (driver.find_element(By.XPATH, "//span[@class = 'LrzXr']").text)
                except:
                    pass
                # Add the district name to the DataFrame
                df["district"][index] = dis
                index += 1
            except:
                pass
        
        # Click on the next page of search results
        try:
            driver.find_element(By.XPATH, "//span[@style ='display:block;margin-left:53px']").click()
            time.sleep(2)
        except:
            break
    
    print("Ended District", dis)
    print("Last shape of dataframe -", temp.shape)
    print("Remaining Rows -", 746 - newPop[population["District"] == dis].index[0])

# Filter out rows with missing restaurant names
df = df[~df["name"].isna()]

# Save restaurant data to a CSV file
df.to_csv("restaurant.csv", index=False)

# Drop duplicate rows from the DataFrame
df.drop_duplicates(inplace=True)

# Reset the DataFrame index
df.reset_index(drop=True, inplace=True)

# Remove extra characters from restaurant ratings
df.ratings = df.ratings.str.strip(")")
df.ratings = df.ratings.str.strip("(")

# Fill missing restaurant ratings with 0
df.ratings.fillna("0", inplace=True)

# Convert restaurant ratings to numeric format
df.ratings = df.ratings.apply(lambda x: float(x.replace("T", "")) * 1000 if "T" in x else float(x))

# Define a function to remove text in square brackets from a string
def remove_brackets(x):
    try:
        return re.sub(r'\[.*?\]', '', x)
    except:
        return x

# Apply the remove_brackets function to clean population data
population['Population'] = population['Population'].apply(remove_brackets)
population['Area'] = population['Area'].apply(remove_brackets)
population['Density'] = population['Density'].apply(remove_brackets)

# Remove rows with missing values and reset the index
population = population.dropna().reset_index(drop=True)

# Split the state and state code into separate columns
population[["State", "StateCode"]] =  pd.DataFrame(population.state.str.split("(").to_list(), index=population.index)
population.StateCode = population.StateCode.str.replace(")", "")

# Drop rows with invalid data
population = population.drop([72, 193, 110, 613, 489]).reset_index(drop=True)

# Merge restaurant data with population data based on the district
dfFinal = df.merge(population.rename(columns={"District": "district"}), on="district")

# Rename columns for consistency
dfFinal  = dfFinal.rename(columns={"name": "Restaurant Name"})

# Capitalize column names
dfFinal.columns = [column.capitalize() for column in dfFinal.columns]

# Extract pincode from the address
dfFinal["Pincode"] = dfFinal["Address"].str[-6:]

# Strip leading and trailing whitespaces from state names
dfFinal["State"] = dfFinal["State"].str.strip()

# Filter out rows with missing restaurant names
dfFinal = dfFinal[~dfFinal["Restaurant Name"].isna()]

# Fill missing values in the "Rate" column with 0
dfFinal["Rate"] = dfFinal["Rate"].fillna(0)

# Save the final restaurant data to CSV and Excel files
dfFinal.to_csv("restaurantfinal.csv", index=False)
dfFinal.to_excel("restaurantfinal.xlsx", index=False)
