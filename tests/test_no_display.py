# selenium 4
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options

def test_no_display():
    # Arrange
    service = FirefoxService(executable_path=GeckoDriverManager().install())
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(service=service, options=options)
    
    # Act
    driver.get("https://www.python.org/")
    title = driver.title
    driver.close()
    
    # Assert
    assert title == "Welcome to Python.org"
    