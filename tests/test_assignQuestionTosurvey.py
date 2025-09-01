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

@pytest.mark.order(10)
def test_assignQuestionToSurvey(driver):
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

    # --- Aller dans Surveys ---
    surveys_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Surveys']]"))
    )
    surveys_btn.click()
    # --- Sélectionner le survey ---
    survey_row = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//td[.//div[text()='Sondage All-in-One Selenium']]//ancestor::tr"
        ))
    )

    view_btn = survey_row.find_element(By.XPATH, ".//button[@title='View Survey']")
    view_btn.click()

    # --- Attendre que le modal apparaisse ---
    modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))
    )

    # --- Cliquer sur "Add Existing Questions" ---
    add_existing_btn = WebDriverWait(modal, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            ".//button[contains(text(),'Add Existing Questions')]"
        ))
    )
    add_existing_btn.click()

    # --- Attendre que le modal contenant les questions apparaisse ---
    questions_modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))
    )

    # --- Récupérer tous les boutons "Add to Survey" dans ce modal ---
    add_buttons = questions_modal.find_elements(By.XPATH, ".//button[contains(text(),'Add to Survey')]")

    # --- Cliquer sur chaque bouton ---
    for btn in add_buttons:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(btn))
        btn.click()
        time.sleep(0.3)  # petit délai pour laisser le DOM se mettre à jour

    # --- Fermer le modal des questions ---
    close_btn = questions_modal.find_element(By.XPATH, ".//button[contains(text(),'Close')]")
    close_btn.click()

    # --- Vérifier qu'au moins une question est affichée dans la liste du survey ---
    questions_list = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='survey-questions-list']//tr"))
    )
    assert len(questions_list) > 0, "Aucune question n'a été ajoutée au survey"


