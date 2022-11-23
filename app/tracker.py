import utils
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pathlib
import unicodedata
from datetime import date, datetime, timedelta
import database
import sqlalchemy

class ElTracker:
    def __init__(self, region_zone: str, base_url: str) -> None:
        self.base_url = base_url
        self.hourly_url = f"{self.base_url}/Hourly"
        self.daily_url = f"{self.base_url}/Hourly1"
        self.weekly_url = f"{self.base_url}/Weekly"
        self.monthly_url = f"{self.base_url}/Monthly"
        self.region_zone = region_zone
        self.temp_html_file = pathlib.Path(__file__).parent.joinpath("table.html")

    def html_to_soup(self, html: str) -> BeautifulSoup:
        """html_to_soup converts HTML string into a BeautifulSoup object

        Args:
            html (str): raw HTML

        Returns:
            BeautifulSoup: HTML converted to BeautifulSoup object
        """        
        soup = BeautifulSoup(html, "lxml")

        return soup

    def selenium_driver(self, headless: bool = False) -> webdriver.Firefox:
        """selenium_driver creates a Selenium webdriver object.

        Args:
            headless (bool, optional): Determines whether the browser id visible or not. Defaults to False.

        Returns:
            webdriver.Firefox: a Selenium webdriver object.
        """
        service = FirefoxService(executable_path=GeckoDriverManager().install())

        # Set headless option
        options = Options()
        options.headless = headless

        # Initialise selenium driver
        driver = webdriver.Firefox(service=service, options=options)

        return driver
    
    def confirm_mwh_text(self, dashboard_unit_element) -> bool:
        mwh_text_confirmed = False
        currency_element = dashboard_unit_element.find_element(
            By.CLASS_NAME, "dashboard-table-unit.ng-binding"
        )
        utils.print_message(currency_element.text)
        expected_text = "SEK/MWh"
        utils.print_message(f"Expecting {expected_text}")
        if currency_element.text.lower() == expected_text.lower():
            mwh_text_confirmed = True
            utils.print_message(f"Expected text located: {mwh_text_confirmed}")
        else:
            utils.print_message(f"Expected text located: {mwh_text_confirmed}. Found {currency_element.text}")
            
        return mwh_text_confirmed
        

    def get_hourly_data_html(self) -> str:
        driver = self.selenium_driver()
        soup_html = None
        driver.get(self.hourly_url)
        
        # General self.do_wait() variables
        page_wait = 1
        page_wait_message = "Waiting for page"
        
        # click cookies
        utils.do_wait(page_wait, "Waiting for cookie button to appear")
        driver.find_element(By.CLASS_NAME, "pure-button").click()
        utils.print_message("Cookie button should be gone")

        # close message
        utils.do_wait(page_wait, page_wait_message)
        driver.find_element(
            By.CLASS_NAME, "svg.img-close.notificationAcknowledge"
        ).click()
        utils.print_message("Lower notification should gone")
        utils.do_wait(page_wait, page_wait_message)
        driver.find_element(
            By.CLASS_NAME, "svg.img-close.notificationAcknowledge"
        ).click()
        utils.print_message("Upper notification should be gone")

        # Choose region zone e.g. "SE3"
        utils.do_wait(2, page_wait_message)
        driver.find_element(By.LINK_TEXT, self.region_zone).click()
        
        # Choose SEK
        utils.do_wait(page_wait, page_wait_message)
        select = Select(driver.find_element(By.ID, "data-currency-select"))
        select.select_by_visible_text("SEK")

        # Verify SEK/MWh text to make sure we're looking at the correct currency data
        utils.do_wait(page_wait, page_wait_message)
        dashboard_unit_element = driver.find_element(
            By.CLASS_NAME, "dashboard-unit-update"
        )
        mwh_text_confirmed = self.confirm_mwh_text(dashboard_unit_element)
        
        if mwh_text_confirmed:
            # Check updates time stamp
            ts_element = driver.find_element(By.CLASS_NAME, "updated-timestamp")
            ts_element.find_element(By.CLASS_NAME, "ng-binding")
            last_update_text = ts_element.text  # .split(":")[-1].strip()
            utils.print_message(f"Found last update text {last_update_text}")

            last_update_text = last_update_text.split("Last update: ")[-1]
            utils.print_message(f"Parsed last update text {last_update_text}")

            last_update_text_split = last_update_text[:-1].split(" ")
            utils.print_message(last_update_text_split)

            # Get table HTML
            testing_text = "yesterday"
            if last_update_text_split[0].lower() == "today":
                # if last_update_text_split[0].lower() == testing_text:
                utils.print_message("Today's data is available")

                data_table = driver.find_element(By.ID, "datatable")
                data_table_html = data_table.get_attribute("outerHTML")
                soup = self.html_to_soup(html=data_table_html)
                soup = soup.prettify()
                soup_html = str(soup)

                with open(self.temp_html_file, "w") as f:
                    f.write(soup_html)
            else:
                utils.print_message("Today's data is not available yet")

        else:
            utils.print_message("Did not get table data ")

        # input("Enter to close browser...")
        driver.close()

        return soup_html

    def confirm_region_zone(self, table_region_zone_text: str) -> tuple[bool, str]:
        if table_region_zone_text == self.region_zone:
            region_zone_confirmed = True
        else:
            region_zone_confirmed = False

        utils.print_message(
        f"Region zone confirmed as {self.region_zone}: {region_zone_confirmed}"
        )
        
        return region_zone_confirmed, table_region_zone_text
    
    def confirm_date(self, date_text: str) -> tuple[bool, date]:
        date_text_dt_obj = datetime.strptime(date_text, "%d-%m-%Y").date()
        column_header_date_confirmed_as_tomorrow = False
        today = date.today()
        tomorrow = today + timedelta(days=1)
        if date_text_dt_obj == tomorrow:
            column_header_date_confirmed_as_tomorrow = True
        else:
            column_header_date_confirmed_as_tomorrow = False
        
        utils.print_message(
            f"Tomorrow's date confirmed as {tomorrow}: {column_header_date_confirmed_as_tomorrow}"
        )

        return column_header_date_confirmed_as_tomorrow, date_text_dt_obj
        

    def parse_table_html(self, html: str):
        soup: BeautifulSoup = self.html_to_soup(html)

        # Get column headers to confirm the date and region zone
        table_head = soup.find("thead")
        table_column_headers = table_head.find_all("th")
        table_column_headers_list = [tch.getText().strip() for tch in table_column_headers]
        column_header_date_text = table_column_headers_list[0]
        column_header_region_zone_text = table_column_headers_list[1]

        # Confirm region zone in column header is the one we want ie SE3
        region_zone_confirmed, table_region_zone_text = self.confirm_region_zone(column_header_region_zone_text)

        # Confirm date in column header as tomorrow's
        column_header_date_confirmed_as_tomorrow, date_text_dt_obj = self.confirm_date(column_header_date_text)

        # Looks like region/data you want is available ie SE3 and tomorrow's data
        if region_zone_confirmed and column_header_date_confirmed_as_tomorrow:
            utils.print_message("Getting table data")

            # Do get table data
            table_body = soup.find("tbody")
            table_rows = table_body.find_all("tr")
            for table_row in table_rows:
                row = table_row.find_all("td")

                column1 = row[0].getText().strip()
                column2 = row[1].getText().strip().replace(" ", "").replace(",", ".")

                if len(column1) > 0 and len(column2) > 0:
                    try:
                        col1_split = column1.split("-")
                        start_hour = int(col1_split[0].strip())
                        end_hour = int(col1_split[1].strip())
                        sek_per_megawatt_hour = float(column2)
                        sek_per_kilowatt_hour = round(sek_per_megawatt_hour / 1000, 2)
                        date_start_hour = f"{date_text_dt_obj.strftime('%Y%m%d')}{start_hour}"
                        date_start_hour = int(date_start_hour)
                        d = {
                            "date": column_header_date_text,
                            "time_period": f"{start_hour}-{end_hour}",
                            "sek_per_kwh": sek_per_kilowatt_hour,
                            "start_hour": start_hour,
                            "end_hour": end_hour,
                            "date_start_hour": date_start_hour
                        }
                        # pprint(d, indent=4)
                        query = database.db.insert(database.day_ahead).values(
                            date_start_hour=date_start_hour,
                            date=date_text_dt_obj,
                            start_hour=start_hour,
                            end_hour=end_hour,
                            sek_per_kwh=sek_per_kilowatt_hour
                        )
                        # print(f"{column_header_date_text} {start_hour}-{end_hour} kWh: {sek_per_kilowatt_hour}")
                        try:
                            # Add data to database
                            database.connection.execute(query)
                            utils.print_message(f"Added {date_start_hour} prices to DB")
                        except sqlalchemy.exc.IntegrityError as e:
                            utils.print_message(f"{type(e)} - {str(e)}")
                    except (ValueError, IndexError):
                        pass
                        # print(f"{column1} - kWh: {kilowatt_hour}")
        
        # Looks like region/data you want is NOT available ie SE3 and tomorrow's data
        else:
            if (
                region_zone_confirmed is False
                and column_header_date_confirmed_as_tomorrow is True
            ):
                utils.print_message(
                    f"Region zone is wrong. Expecting {self.region_zone}. Got {table_region_zone_text}"
                )
            elif (
                region_zone_confirmed is True
                and column_header_date_confirmed_as_tomorrow is False
            ):
                utils.print_message(
                    "Date in column header is not tomorrow's: {date_text_dt_obj}"
                )
            else:
                utils.print_message(
                    f"Region zone is wrong. Expecting {self.region_zone}. Got {table_region_zone_text}"
                )
                utils.print_message(
                    "Date in column header is not tomorrow's: {date_text_dt_obj}"
                )

        # return None

    def main(self, check_website=False):
        if check_website is False:
            utils.print_message(f"Checking {self.temp_html_file} for price data")
            with open(self.temp_html_file) as f:
                hourly_data_html = f.read()
        else:
            utils.print_message(f"Checking {self.hourly_url} for price data")
            hourly_data_html = self.get_hourly_data_html()
            
        table_soup = self.parse_table_html(html=hourly_data_html)


e = ElTracker(
    region_zone="SE3",
    base_url="https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/SE"
)
e.main()
