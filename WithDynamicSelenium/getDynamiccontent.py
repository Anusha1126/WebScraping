import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

class EbayScraper:
    def __init__(self, search_query, driver_path= r'chromedriver.exe', num_results=10):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_driver_path = os.path.join(script_dir, driver_path)
        driver_path=full_driver_path
        self.search_query = search_query
        self.driver_path = driver_path
        self.num_results = num_results
        self.driver = None

    def initialize_driver(self):
        service = Service(executable_path=self.driver_path)
        self.driver = webdriver.Chrome(service=service)

    def search_items(self):
        self.driver.get("https://www.ebay.com")
        search_element = self.driver.find_element(By.XPATH, '//input[@class="gh-tb ui-autocomplete-input"]')
        search_element.clear()
        search_element.send_keys(self.search_query)
        self.driver.find_element(By.XPATH, '//input[@class="btn btn-prim gh-spr"]').click()
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "s-item")))

    def scrape_results(self):
        title_elements = self.driver.find_elements(By.CLASS_NAME, "s-item__title")
        price_elements = self.driver.find_elements(By.CLASS_NAME, "s-item__price")

        book_titles = []
        product_prices = []

        for title_element, price_element in zip(title_elements, price_elements):
            title_text = title_element.text.strip()
            price_text = price_element.text.strip()
            if title_text and price_text:
                cleaned_title = re.sub(r"[^\w\s]", "", title_text)
                cleaned_price = re.sub(r"[$,]", "", price_text)
                book_titles.append(cleaned_title)
                product_prices.append(cleaned_price)
            
            if len(book_titles) >= self.num_results:
                break

        return book_titles, product_prices

    def save_to_csv(self, titles, prices, filename='products.csv'):
        df = pd.DataFrame({'Title': titles, 'Price': prices})
        df.to_csv(filename, index=False)

    def close_driver(self):
        self.driver.quit()

    def scrape_and_save(self):
        self.initialize_driver()
        self.search_items()
        titles, prices = self.scrape_results()
        self.save_to_csv(titles, prices)
        self.close_driver()
        print(f"Collected {len(titles)} titles and {len(prices)} prices.")
        print(pd.DataFrame({'Title': titles, 'Price': prices}))

if __name__ == "__main__":
    scraper = EbayScraper(search_query="programming books")
    scraper.scrape_and_save()
