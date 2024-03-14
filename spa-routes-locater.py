from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
import logging
import csv

# Setup logging
logging.basicConfig(filename='sparoutefinder.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

class SPARouteFinder:
    def __init__(self, start_url):
        self.start_url = start_url
        self.visited_routes = set()
        self.driver = webdriver.Chrome()  # Change this line based on your WebDriver
        self.wait = WebDriverWait(self.driver, 10)

    def find_routes(self):
        self._explore_route(self.start_url)

        self.driver.quit()
        logging.info("Discovered routes: %s", self.visited_routes)
        print("Discovered routes:", self.visited_routes)

        self._save_routes_to_csv()

    def _explore_route(self, url):
        self.driver.get(url)
        self._wait_for_page_load()

        if url not in self.visited_routes:
            self.visited_routes.add(url)
            elements = self.driver.find_elements(By.XPATH, "//*")  # Targeting links and buttons

            for i in range(len(elements)):
                try:
                    elements = self.driver.find_elements(By.XPATH, "//*")  # Refresh elements list to avoid stale references
                    element = elements[i]

                    if self._is_clickable(element):
                        initial_url = self.driver.current_url
                        ActionChains(self.driver).move_to_element(element).click(element).perform()  # Using ActionChains for more accurate clicks
                        self._wait_for_page_load()

                        new_url = self.driver.current_url
                        if new_url != initial_url and new_url not in self.visited_routes:
                            logging.info("Found new route: %s", new_url)
                            self._explore_route(new_url)

                        self.driver.get(url)
                        self._wait_for_page_load()
                except StaleElementReferenceException:
                    logging.warning("Encountered a stale element reference. Continuing with the next element.")
                    continue
                except Exception as e:
                    logging.error("Error during navigation: %s", e)

    def _is_clickable(self, element):
        try:
            return element.is_displayed() and element.is_enabled()
        except NoSuchElementException:
            return False

    def _wait_for_page_load(self, timeout=10):
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException:
            logging.warning("Timeout waiting for page to load")

    def _save_routes_to_csv(self):
        with open('asure-win-test.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Discovered Routes"])
            for route in self.visited_routes:
                writer.writerow([route])
        logging.info("Routes saved to discovered_routes.csv")

if __name__ == "__main__":
    start_url = "http://example.com"  # Replace with the actual start URL of the SPA
    spa_finder = SPARouteFinder(start_url)
    spa_finder.find_routes()