from seleniumbase import Driver

def wait_for_elements(driver, by, selector, timeout=10, multiple=False):
    """Wait for elements to be present and return them"""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    wait = WebDriverWait(driver, timeout)
    if multiple:
        elements = wait.until(EC.presence_of_all_elements_located((by, selector)))
        return elements
    else:
        element = wait.until(EC.presence_of_element_located((by, selector)))
        return element

def click_element(driver, by, selector):
    """Find an element and click it"""
    try:
        element = wait_for_elements(driver, by, selector, multiple=False)
        element.click()
        return True
    except Exception as e:
        print(f"Error clicking element: {e}")
        return False

def initialize_driver():
    """Initialize the Selenium driver with necessary configurations"""
    driver = Driver(
        browser="chrome",
        uc=True,
        headless2=True,  # Set to True for headless mode
        incognito=False,
        agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        do_not_track=True,
        undetectable=True
    )
    driver.maximize_window()
    return driver