import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Fixture pour initialiser et fermer le navigateur
@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    yield driver
    driver.quit()

# Test login correct
@pytest.mark.order(3)
def test_login_success(driver):
    driver.get("http://localhost:3000/")

    # Saisie email
    email = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email.send_keys("oumaima@gmail.com")

    # Saisie mot de passe
    password = driver.find_element(By.NAME, "password")
    password.send_keys("oumaima")

     # Cliquer sur Sign In
    sign_in = driver.find_element(By.XPATH, "//button[text()='Sign In']")
    sign_in.click()

    # Attendre la redirection vers le dashboard (par URL)
    WebDriverWait(driver, 10).until(lambda d: "/dashboard" in d.current_url)
    assert "/dashboard" in driver.current_url

    # Optionnel : vérifier qu'un élément unique du dashboard est affiché
    dashboard_header = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h1[text()='Dashboard']"))
    )
    assert dashboard_header.is_displayed()

# Test login incorrect
@pytest.mark.order(5)
def test_login_wrong_password(driver):
    driver.get("http://localhost:3000/")

    # Saisie email
    email = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email.send_keys("testuser@example.com")

    # Saisie mot de passe incorrect
    password = driver.find_element(By.NAME, "password")
    password.send_keys("wrongpassword")

    # Cliquer sur le bouton Sign In
    sign_in = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    sign_in.click()

    # Attendre le message d'erreur
    error_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.text-red-700"))
    )
    assert error_message.is_displayed()
