import time
import random
import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import logging

# Import utility functions
from Scrapers.utils.parser import wait_for_elements, initialize_driver

class MercadonaScraper:
    """Selenium-based scraper for Mercadona products"""
    
    def __init__(self, output_dir="data/raw", postal_code="03005"):
        """Initialize the scraper"""
        self.output_dir = output_dir
        self.postal_code = postal_code
        
        # Set up logging
        self.logger = logging.getLogger('mercadona_scraper')
        self.logger.setLevel(logging.INFO)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Driver will be initialized when needed
        self.driver = None
    
    def get_product_data(self, category_name):
        """Extract product data from the current page"""
        products = []
        try:
            product_elements = wait_for_elements(self.driver, By.CSS_SELECTOR, 
                                                'div.product-cell[data-testid="product-cell"]', 
                                                multiple=True)
            self.logger.info(f"Found {len(product_elements)} products in {category_name}")

            for product in product_elements:
                html_content = product.get_attribute('innerHTML')
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract product name
                name_element = soup.find('h4', class_="subhead1-r product-cell__description-name", 
                                        attrs={"data-testid": "product-cell-name"})
                name = name_element.text if name_element else "Name not available"

                # Extract price (handling both regular and discount prices)
                price_element = soup.find('p', class_="product-price__unit-price subhead1-b", 
                                        attrs={"data-testid": "product-price"})
                if price_element is None:
                    price_element = soup.find('p', 
                                            class_="product-price__unit-price subhead1-b product-price__unit-price--discount", 
                                            attrs={"data-testid": "product-price"})
                
                price = price_element.text.replace(".", "").replace(",", ".").replace("€", "").strip() if price_element else "Price not available"

                # Extract price per unit
                price_per_unit_element = soup.find('p', class_="product-price__size-price body2-r")
                price_per_unit = price_per_unit_element.text.strip() if price_per_unit_element else "N/A"
                
                # Extract product image URL if available
                image_element = soup.find('img', class_="product-cell__image-container__image")
                image_url = image_element.get('src') if image_element else ""
                
                # Extract product weight/quantity if available
                quantity_element = soup.find('p', class_="product-cell__description-format body2-r")
                quantity = quantity_element.text.strip() if quantity_element else ""

                products.append({
                    'name': name,
                    'price': price,
                    'price_per_unit': price_per_unit,
                    'category': category_name,
                    'image_url': image_url,
                    'quantity': quantity,
                    'scraped_date': datetime.now().strftime("%Y-%m-%d")
                })
                
        except TimeoutException:
            self.logger.warning(f"No products found in {category_name}")
        except Exception as e:
            self.logger.error(f"Error getting product data: {e}")
            
        return products

    def explore_categories(self):
        """Explore all categories and extract product data"""
        all_products = []
        self.driver.get("https://tienda.mercadona.es/categories/112")
        time.sleep(3)  # Wait longer for initial page load
        
        try:
            # Find all main categories
            main_categories = wait_for_elements(self.driver, By.CSS_SELECTOR, '.category-menu__header', multiple=True)
            self.logger.info(f"Found {len(main_categories)} main categories")
            
            for category_index, category in enumerate(main_categories):
                try:
                    # Get category name
                    category_name = category.text.replace(",", "").strip()
                    self.logger.info(f"\nExploring main category {category_index+1}/{len(main_categories)}: {category_name}")
                    
                    # Click on the category to open it
                    time.sleep(random.uniform(1, 2))
                    category.click()
                    time.sleep(random.uniform(1, 2))
                    
                    # Get the opened category container
                    try:
                        open_category = wait_for_elements(self.driver, By.CSS_SELECTOR, 
                                                         'li.category-menu__item.open', 
                                                         multiple=False, timeout=5)
                        
                        # Find all subcategories
                        subcategories = wait_for_elements(open_category, By.CSS_SELECTOR, 
                                                         'ul > li.category-item', multiple=True)
                        self.logger.info(f"Found {len(subcategories)} subcategories in {category_name}")
                        
                        for subcategory_index, subcategory in enumerate(subcategories):
                            subcategory_name = subcategory.text.strip()
                            self.logger.info(f"  Exploring subcategory {subcategory_index+1}/{len(subcategories)}: {subcategory_name}")
                            
                            try:
                                # Click on subcategory to view products
                                time.sleep(random.uniform(1, 2))
                                subcategory.click()
                                time.sleep(random.uniform(2, 3))
                                
                                # Extract current URL to check category ID
                                current_url = self.driver.current_url
                                category_id = current_url.split('/')[-1] if 'categories' in current_url else 'Unknown'
                                self.logger.info(f"    Category ID: {category_id}")
                                
                                # Get product data
                                full_category_path = f"{category_name} > {subcategory_name}"
                                products = self.get_product_data(full_category_path)
                                all_products.extend(products)
                                
                                # Check for pagination and navigate through pages if available
                                try:
                                    pagination = self.driver.find_elements(By.CSS_SELECTOR, '.pagination__page')
                                    if len(pagination) > 1:
                                        self.logger.info(f"    Found {len(pagination)} pages")
                                        # Process additional pages
                                        for page_num in range(2, len(pagination) + 1):
                                            try:
                                                page_button = self.driver.find_element(
                                                    By.XPATH, f"//button[@aria-label='Go to page {page_num}']")
                                                page_button.click()
                                                time.sleep(random.uniform(2, 3))
                                                self.logger.info(f"    Processing page {page_num}")
                                                page_products = self.get_product_data(
                                                    f"{full_category_path} (Page {page_num})")
                                                all_products.extend(page_products)
                                            except Exception as e:
                                                self.logger.error(f"    Error navigating to page {page_num}: {e}")
                                except Exception:
                                    # No pagination or error finding pagination
                                    pass
                                    
                            except Exception as e:
                                self.logger.error(f"  Error processing subcategory {subcategory_name}: {e}")
                                
                    except TimeoutException:
                        self.logger.warning(f"No subcategories found in {category_name} or category didn't open properly")
                    except Exception as e:
                        self.logger.error(f"Error getting subcategories for {category_name}: {e}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing main category: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error during category exploration: {e}")
            
        return all_products

    def handle_postal_code_entry(self):
        """Handle the postal code entry process"""
        try:
            self.logger.info("Trying to enter postal code...")
            
            # Check if we need to enter postal code
            postal_code_input = None
            try:
                postal_code_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="postalCode"]')
            except Exception:
                self.logger.info("No postal code input found, we may be already logged in.")
            
            if postal_code_input:
                # Clear and enter postal code
                postal_code_input.clear()
                postal_code_input.send_keys(self.postal_code)
                self.logger.info(f"Entered postal code: {self.postal_code}")
                
                # Try different methods to submit the postal code
                # Method 1: Click the postal code submit button if found
                try:
                    # Try multiple selectors
                    submit_button = None
                    selectors = [
                        'button[type="submit"]',
                        'form button',
                        'button.button-primary',
                        'button.postal-code-form__button',
                        'button[data-testid="postal-code-form-submit-button"]'
                    ]
                    
                    for selector in selectors:
                        try:
                            submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if submit_button and submit_button.is_displayed():
                                self.logger.info(f"Found submit button using selector: {selector}")
                                break
                        except:
                            continue
                    
                    if submit_button and submit_button.is_displayed():
                        # Scroll to make it visible
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                        time.sleep(1)
                        
                        # Try direct click
                        submit_button.click()
                        self.logger.info("Clicked submit button directly")
                    else:
                        self.logger.info("Submit button not found, trying JavaScript click")
                        # Method 2: JavaScript click
                        self.driver.execute_script("""
                            var buttons = document.querySelectorAll('button');
                            for(var i=0; i<buttons.length; i++) {
                                if(buttons[i].textContent.includes('Empezar') || 
                                   buttons[i].textContent.includes('Entrar') ||
                                   buttons[i].textContent.includes('Comprar') ||
                                   buttons[i].textContent.includes('Submit') ||
                                   buttons[i].type === 'submit') {
                                    buttons[i].click();
                                    return true;
                                }
                            }
                            return false;
                        """)
                        self.logger.info("Attempted JavaScript button click")
                
                except Exception as e:
                    self.logger.error(f"Error clicking submit button: {e}")
                    
                    # Method 3: Enter key
                    try:
                        postal_code_input.send_keys(Keys.RETURN)
                        self.logger.info("Submitted form using Enter key")
                    except Exception as e:
                        self.logger.error(f"Error submitting with Enter key: {e}")
                
                # Wait for navigation
                time.sleep(5)
                self.logger.info(f"Current URL after postal code entry: {self.driver.current_url}")
                
                # Check if store selection is needed
                try:
                    store_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        '.store-selection__store-button, .store-item, [data-testid="store-item"]'
                    )
                    if store_elements and len(store_elements) > 0:
                        self.logger.info(f"Found {len(store_elements)} stores. Selecting the first one.")
                        store_elements[0].click()
                        time.sleep(3)
                except Exception as e:
                    self.logger.info(f"No store selection needed or error: {e}")
        
        except Exception as e:
            self.logger.error(f"Error in postal code entry process: {e}")
            self.save_debug_screenshot("postal_code_error.png")

    def handle_cookies(self):
        """Accept cookies if prompted"""
        try:
            cookie_selectors = [
                "//button[normalize-space()='Aceptar']",
                "//button[contains(text(), 'cookie')]",
                "//button[contains(text(), 'Cookie')]",
                "//button[contains(@class, 'cookie')]",
                "//div[contains(@class, 'cookie')]//button"
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_buttons = self.driver.find_elements(By.XPATH, selector)
                    if cookie_buttons and len(cookie_buttons) > 0:
                        for button in cookie_buttons:
                            if button.is_displayed():
                                button.click()
                                self.logger.info(f"Accepted cookies using selector: {selector}")
                                time.sleep(2)
                                break
                except:
                    continue
        except Exception as e:
            self.logger.error(f"Error handling cookies: {e}")

    def save_debug_screenshot(self, filename):
        """Save a screenshot for debugging purposes"""
        try:
            screenshot_path = os.path.join(self.output_dir, "debug", filename)
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"Screenshot saved as {screenshot_path}")
        except Exception as e:
            self.logger.error(f"Could not save screenshot: {e}")

    def save_products_to_csv(self, products):
        """Save products to CSV file"""
        if not products:
            self.logger.warning("No products to save.")
            return None
            
        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = f"mercadona_products_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create DataFrame and save
        df = pd.DataFrame(products)
        df.to_csv(filepath, index=False)
        self.logger.info(f"Saved {len(products)} products to {filepath}")
        
        # Create a copy with a fixed name for the application
        latest_filepath = os.path.join(self.output_dir, "mercadona_products_latest.csv")
        df.to_csv(latest_filepath, index=False)
        self.logger.info(f"Also saved to {latest_filepath} for application use")
        
        return filepath

    def run(self):
        """Run the full scraping process"""
        self.logger.info(f"Starting Mercadona scraping at: {datetime.now()}")
        self.driver = initialize_driver()
        all_products = []
        
        try:
            # Navigate to Mercadona website
            self.driver.get("https://tienda.mercadona.es/")
            time.sleep(3)
            
            # Handle postal code entry and cookies
            self.handle_postal_code_entry()
            self.handle_cookies()
            
            # Debug logging
            self.logger.info(f"Current URL before exploring categories: {self.driver.current_url}")
            self.save_debug_screenshot("before_categories.png")
            
            # Explore categories and get products
            all_products = self.explore_categories()
            
            # Save products to CSV
            filepath = self.save_products_to_csv(all_products)
            
            return len(all_products)
            
        except Exception as e:
            self.logger.error(f"Error during scraping process: {e}")
            self.save_debug_screenshot("error_screenshot.png")
            return 0
            
        finally:
            # Always close the driver
            if self.driver:
                self.driver.quit()


# Direct execution for testing or standalone use
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("mercadona_scraper.log"),
            logging.StreamHandler()
        ]
    )
    
    scraper = MercadonaScraper()
    product_count = scraper.run()
    logging.info(f"Scraping completed. Total products collected: {product_count}")