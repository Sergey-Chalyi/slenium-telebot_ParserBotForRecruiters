from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from dataclasses import dataclass
from typing import List, Dict, Optional
import json
import logging


@dataclass
class ResumeData:
    """Data structure for storing resume information"""
    update_date: str
    name: str
    specialization: str
    salary: str
    url: str


class WorkUaParser:
    """Parser for work.ua website"""

    BASE_URL = "https://www.work.ua/resumes/by-category/"
    WAIT_TIMEOUT = 10

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.WAIT_TIMEOUT)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()


    def get_categories(self) -> List[Dict[str, str]]:
        """Get all available resume categories"""
        self.driver.get(self.BASE_URL)
        categories = self.driver.find_elements(By.XPATH, "//li/a[starts-with(@href, '/resumes-')]")

        return [
            {"name": cat.text, "url": cat.get_attribute("href"), "index": idx + 1}
            for idx, cat in enumerate(categories)
        ]

    def select_category(self, category_index: int):
        """Select category by its index"""
        categories = self.get_categories()
        if 1 <= category_index <= len(categories):
            selected_category = categories[category_index - 1]
            self.driver.get(selected_category["url"])
        else:
            raise ValueError(f"Category index should be between 1 and {len(categories)}")


    def wait_and_find_element(self, by, value, timeout=WAIT_TIMEOUT):
        """Wait for element to be present and return it"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_and_find_elements(self, by, value, timeout=WAIT_TIMEOUT):
        """Wait for elements to be present and return them"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )

    def wait_for_page_update(self):
        """Wait for page update after filter change"""
        try:
            # Store the current page source
            old_page = self.driver.page_source

            # Wait for page source to change
            def page_changed(driver):
                return driver.page_source != old_page

            WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(page_changed)

            # Wait for the loading overlay to disappear (if exists)
            try:
                WebDriverWait(self.driver, 3).until_not(
                    EC.presence_of_element_located((By.CLASS_NAME, "loading-overlay"))
                )
            except TimeoutException:
                pass  # Ignore if no loading overlay found


        except TimeoutException:
            logging.warning("Page update timeout - continuing anyway")


    def choose_profession(self, profession: str):
        self.driver.find_element(By.XPATH, '//*[@id="search"]').send_keys(profession)

    def choose_location(self, location: str):
        city_input = self.driver.find_element(By.XPATH, '//*[@id="city"]')
        city_input.click()
        city_input.send_keys(Keys.CONTROL, 'a')
        city_input.send_keys(Keys.DELETE)
        city_input.send_keys(location)

    def handle_filter_action(self, action_func):
        """
        Execute a filter action and wait for page update

        Args:
            action_func: Function that performs the filter action
        """
        try:
            # Execute the filter action
            action_func()
            # Wait for page to update
            self.wait_for_page_update()
        except Exception as e:
            logging.error(f"Error during filter action: {str(e)}")


    def apply_filters(self, filters: Dict):
        try:
            if 'search_params' in filters:
                self.apply_search_filters(filters['search_params'])

            if 'employment' in filters:
                self.apply_employment_filters(filters['employment'])

            if 'age' in filters:
                self.apply_age_filters(filters['age'])

            if 'gender' in filters:
                self.apply_gender_filters(filters['gender'])

            if 'salary' in filters:
                self.apply_salary_filters(filters['salary'])

            if 'education' in filters:
                self.apply_education_filters(filters['education'])

            if 'experience' in filters:
                self.apply_experience_filters(filters['experience'])

        except TimeoutException as e:
            logging.error(f"Timeout while applying filters: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error applying filters: {str(e)}")
            raise

    def is_checkbox_selected(self, xpath: str) -> bool:
        """
        Check if a checkbox is already selected.

        Args:
            xpath: The xpath of the checkbox element

        Returns:
            bool: True if the checkbox is already selected, False otherwise
        """
        checkbox = self.wait_and_find_element(By.XPATH, xpath)
        return checkbox.is_selected()

    def apply_search_filters(self, search_params: List[str]):
        search_params_map = {
            'title_only': "//input[@id='f1-1']",
            'with_synonyms': "//input[@id='f2-2']",
            'any_word': "//input[@id='f3-3']"
        }
        for param in search_params:
            if param in search_params_map:
                xpath = search_params_map[param]
                if not self.is_checkbox_selected(xpath):
                    self.handle_filter_action(
                        lambda: self.wait_and_find_element(By.XPATH, xpath).click()
                    )


    def apply_employment_filters(self, employment: List[str]):
        employment_map = {
            'full_time': "//*[@id='employment_selection']/ul[1]/li/label/input",
            'part_time': "//*[@id='employment_selection']/ul[2]/li/label/input"
        }
        for emp_type in employment:
            if emp_type in employment_map:
                xpath = employment_map[emp_type]
                # Check if already selected
                if not self.is_checkbox_selected(xpath):
                    self.handle_filter_action(
                        lambda: self.wait_and_find_element(By.XPATH, xpath).click()
                    )

    def apply_age_filters(self, age: Dict[str, int]):
        if 'from' in age:
            self.handle_filter_action(
                lambda: Select(self.wait_and_find_element(
                    By.XPATH, "//select[@id='agefrom_selection']"
                )).select_by_value(str(age['from']))
            )
        if 'to' in age:
            self.handle_filter_action(
                lambda: Select(self.wait_and_find_element(
                    By.XPATH, "//select[@id='ageto_selection']"
                )).select_by_value(str(age['to']))
            )

    def apply_gender_filters(self, gender: List[str]):
        gender_map = {
            'male': "//*[@id='gender_selection']/ul[1]/li/label/input",
            'female': "//*[@id='gender_selection']/ul[2]/li/label/input"
        }
        for g in gender:
            if g in gender_map:
                xpath = gender_map[g]
                # Check if already selected
                if not self.is_checkbox_selected(xpath):
                    self.handle_filter_action(
                        lambda: self.wait_and_find_element(By.XPATH, xpath).click()
                    )

    def apply_salary_filters(self, salary: Dict[str, str]):
        salary_value_map = {
            10000: "2",
            15000: "3",
            20000: "4",
            30000: "5",
            40000: "6",
            50000: "7",
            100000: "8"
        }

        # Если указан диапазон зарплаты "от"
        if 'from' in salary:
            from_value = salary_value_map.get(salary['from'])  # Преобразуем значение зарплаты в ключ словаря
            if from_value:
                self.handle_filter_action(
                    lambda: Select(self.wait_and_find_element(
                        By.XPATH, "//*[@id='salaryfrom_selection']"
                    )).select_by_value(from_value)
                )

        # Если указан диапазон зарплаты "до"
        if 'to' in salary:
            to_value = salary_value_map.get(salary['to'])  # Преобразуем значение зарплаты в ключ словаря
            if to_value:
                self.handle_filter_action(
                    lambda: Select(self.wait_and_find_element(
                        By.XPATH, "//*[@id='salaryto_selection']"
                    )).select_by_value(to_value)
                )

        # Если указано, что зарплата "не указана"
        if salary.get('not_specified'):
            xpath = "//*[@id='nosalary_selection']/label/input"
            if not self.is_checkbox_selected(xpath):
                self.handle_filter_action(
                    lambda: self.wait_and_find_element(By.XPATH, xpath).click()
                )

    def apply_education_filters(self, education: List[str]):
        education_map = {
            'higher': "//*[@id='education_selection']/li[1]/label/input",
            'unfinished_higher': "//*[@id='education_selection']/li[2]/label/input",
            'specialized_secondary': "//*[@id='education_selection']/li[3]/label/input",
            'secondary': "//*[@id='education_selection']/li[4]/label/input"
        }
        for edu_type in education:
            if edu_type in education_map:
                xpath = education_map[edu_type]
                # Check if already selected
                if not self.is_checkbox_selected(xpath):
                    self.handle_filter_action(
                        lambda: self.wait_and_find_element(By.XPATH, xpath).click()
                    )

    def apply_experience_filters(self, experience: List[str]):
        experience_map = {
            'no_experience': "//*[@id='experience_selection']/li[1]/label/input",
            'up_to_1': "//*[@id='experience_selection']/li[2]/label/input",
            '1_to_2': "//*[@id='experience_selection']/li[3]/label/input",
            '2_to_5': "//*[@id='experience_selection']/li[4]/label/input",
            'more_than_5': "//*[@id='experience_selection']/li[5]/label/input"
        }
        for exp_type in experience:
            if exp_type in experience_map:
                xpath = experience_map[exp_type]
                # Check if already selected
                if not self.is_checkbox_selected(xpath):
                    self.handle_filter_action(
                        lambda: self.wait_and_find_element(By.XPATH, xpath).click()
                    )

    def get_resumes_from_pages(self) -> List[ResumeData]:
        """Get all resumes from the current page"""
        resume_links = self.wait_and_find_elements(By.XPATH, "//a[starts-with(@href, '/resumes/')]")[1:]
        resumes = []

        for link in resume_links:
            url = link.get_attribute("href")
            if not url or "/resumes/by-" in url:  # Skip category links
                continue

            # Store the current window handle
            main_window = self.driver.current_window_handle

            # Open resume in new window
            self.driver.execute_script(f"window.open('{url}', '_blank');")

            # Switch to the new window
            self.driver.switch_to.window(self.driver.window_handles[-1])

            try:
                # Extract resume data with waits
                update_date = self.wait_and_find_element(By.XPATH, "//time").get_attribute("datetime")
                name = self.wait_and_find_element(By.XPATH, "//div[1]/div/div/h1[contains(@class, 'mt-0') and contains(@class, 'mb-0')]").text
                specialization_and_salary = self.wait_and_find_element(By.XPATH, "//div[1]/div/div/h2[1]").text

                resume = ResumeData(
                    update_date=update_date,
                    name=name,
                    specialization=specialization_and_salary.split(',')[0],
                    salary=specialization_and_salary.split(',')[1].strip(),
                    url=url,
                )
                resumes.append(resume)


            except Exception as e:
                logging.error(f"Error parsing resume at {url}: {str(e)}")

            finally:
                # Close the resume window and switch back to main window
                self.driver.close()
                self.driver.switch_to.window(main_window)

        return resumes

    def save_to_json(self, resumes: List[ResumeData], filename: str):
        """Save parsed resumes to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(
                [vars(resume) for resume in resumes],
                f,
                ensure_ascii=False,
                indent=2
            )