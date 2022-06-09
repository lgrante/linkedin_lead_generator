import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import csv



# Path to Chrome executable
CHROME_DRIVER_PATH = './chromedriver'

# Instanciate Chrome
driver = webdriver.Chrome(CHROME_DRIVER_PATH)


def linkedin_login(email: str, password: str) -> None:
    # Get email and password inputs and sign in button elements
    email_input = driver.find_element_by_id('session_key')
    password_input = driver.find_element_by_id('session_password')
    signin_button = driver.find_element_by_class_name('sign-in-form__submit-button')

    # Write email and passwords
    email_input.send_keys(email)
    password_input.send_keys(password)

    # Click on sign in button
    signin_button.click()


def profile_search(keywords: [str]) -> [str]:
    search_query = 'site:linkedin.com/in/'
    search_input = driver.find_element_by_name('q')

    for keyword in keywords:
        search_query += f' AND "{keyword}"'

    search_input.send_keys(search_query)
    search_input.send_keys(Keys.RETURN)

    linkedin_links = driver.find_elements(by=By.XPATH, value='//div[contains(@class, "yuRUbf")]/a')
    linkedin_urls = [link.get_attribute('href') for link in linkedin_links]
    
    return linkedin_urls


def create_lead(profile_url: str) -> dict[str, str]:
    driver.get(profile_url)

    sleep(3)

    name = driver.find_element_by_xpath('//div[contains(@class, "pv-text-details__left-panel")]/div[1]/h1')
    job = driver.find_element_by_xpath('//div[contains(@class, "pv-text-details__left-panel")]/div[2]')
    company = driver.find_element_by_css_selector('div[aria-label="Current company"]')
    location = driver.find_element_by_xpath('//div[contains(@class, "pv-text-details__left-panel")]/span[1]')

    return {
        'name': name.text.strip() if name else 'No results',
        'job': job.text.strip() if job else 'No results',
        'company': company.text.strip() if company else 'No results',
        'location': location.text.strip() if location else 'No results'
    }


def main():
    if len(sys.argv) < 4:
        print('python main.py [your_linkedin_email] [your_linkedin_password] [...keywords]\n\n')
        print('Exemple: python main.py myemail@mail.com superpwd CTO Paris startup')
        return

    # Get email and password passed as parameters    
    email = sys.argv[1]
    password = sys.argv[2]
    keywords = sys.argv[3:]

    # Go to LinkedIn website
    driver.get('https://linkedin.com')

    # Login to LinkedIn
    linkedin_login(email, password)

    # Open a new tab and open Google
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't') 
    driver.get('https://google.com')
    driver.find_element_by_xpath('//div[text()="Reject all"]').click()

    # Perform a research on LinkedIn matching with keywords passed as parameters.
    urls = profile_search(keywords)

    # Create the CSV file to store the leads.
    writer = csv.writer(open('leads.csv', 'w'))
    writer.writerow(['Name', 'Job', 'Company', 'Location'])

    for url in urls:
        lead = create_lead(url)
        writer.writerow([lead.get('name'), lead.get('job'), lead.get('company'), lead.get('location')])
    
    driver.quit()


if __name__ == '__main__':
    main()