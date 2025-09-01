import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains



# ------------------------------
# Fixture Selenium avec options
# ------------------------------
@pytest.fixture
def driver():
    chrome_options = Options()
    
    # Désactive la détection Selenium par Chrome
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Lance en mode incognito (évite les mots de passe enregistrés)
    chrome_options.add_argument("--incognito")
    
    # Désactive complètement le gestionnaire de mots de passe
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.mark.order(13)
def test_create_Deparments_Team(driver):
    driver.get("http://localhost:3000/")

    # --- Connexion ---
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email_input.send_keys("oumaima@gmail.com")
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys("oumaima")
    driver.find_element(By.XPATH, "//button[text()='Sign In']").click()
    WebDriverWait(driver, 10).until(lambda d: "/dashboard" in d.current_url)

    # --- Aller dans Department ---
    dep_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Departments']]"))
    )
    dep_btn.click()
    time.sleep(1)

    # --- Cliquer sur le bouton "Create Department" ---
    create_department_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Create Department']"))
    )
    driver.execute_script("arguments[0].click();", create_department_btn)

    # --- Attendre que le modal apparaisse ---
    create_department_modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))  # classe générale du modal
    )
    time.sleep(1)

    # --- Attendre que le champ "Department Name" soit visible ---
    dept_name_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "name"))
    )
    dept_name_input.send_keys("Selenium Department")

    # --- Cliquer sur le bouton "Create Department" du modal ---
    submit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.bg-white form button[type='submit']"))
    )
    driver.execute_script("arguments[0].click();", submit_btn)

    # --- Vérification optionnelle : s'assurer que le département est créé ---
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, "//td//div[contains(text(), 'Selenium Department')]")
        )
    )

    time.sleep(0.1)
    # --- Aller dans Team ---
    team_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Teams']]"))
    )
    team_btn.click()

    # --- Cliquer sur "View Teams" du département Selenium Department ---
    view_teams_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//td[.//div[text()='Selenium Department']]/following-sibling::td//button[@title='View Teams']"
        ))
    )
    driver.execute_script("arguments[0].click();", view_teams_btn)

    # --- Attendre que le modal "Teams" apparaisse ---
    teams_modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'animate-slide-up')]"))
    )

    # --- Cliquer sur le bouton "Add Team" dans le modal ---
    add_team_btn = WebDriverWait(teams_modal, 10).until(
        EC.element_to_be_clickable((By.XPATH, ".//button[.//text()[contains(., 'Add Team')]]"))
    )
    driver.execute_script("arguments[0].click();", add_team_btn)

    # --- Attendre que le formulaire "Add Team" soit visible dans le modal ---
    add_team_form = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//form[.//input[@placeholder='Team name']]"))
    )

    # --- Remplir le nom de l'équipe ---
    team_name_input = add_team_form.find_element(By.XPATH, ".//input[@placeholder='Team name']")
    team_name_input.send_keys("Selenium Team 1")

    # --- Cliquer sur le bouton "Add" pour créer l'équipe ---
    add_button = add_team_form.find_element(By.XPATH, ".//button[normalize-space(text())='Add']")
    driver.execute_script("arguments[0].click();", add_button)

    # Attendre que la nouvelle équipe "Selenium Team 1" apparaisse
    new_team = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[text()='Selenium Team 1']"))
    )
    # --- Assertion pour vérifier que l'équipe a bien été créée ---
    assert new_team.is_displayed(), "La team Selenium Team 1 n'a pas été créée ou n'est pas visible"