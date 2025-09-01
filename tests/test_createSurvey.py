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

@pytest.mark.order(6)
def test_create_multiple_surveys_for_search(driver):
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

    # --- Fonction pour créer un survey ---
    def create_survey(title, response_type):
        # --- Ouvrir la modal ---
        create_survey_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Survey')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_survey_btn)
        create_survey_btn.click()

        modal = WebDriverWait(driver, 10).until(
           EC.presence_of_element_located((By.CLASS_NAME, "fixed"))
        )
        time.sleep(0.5)  # pour que la modal soit prête

        # --- Remplir le formulaire ---
        modal.find_element(By.NAME, "title").send_keys(title)
        modal.find_element(By.NAME, "description").send_keys(f"Description pour {title}")
        modal.find_element(By.NAME, "type").send_keys("FEEDBACK")
        modal.find_element(By.NAME, "responseType").send_keys(response_type)

        deadline_input = modal.find_element(By.ID, "deadline")
        deadline_input.click()
        deadline_input.send_keys("23102025")
        deadline_input.send_keys(Keys.ARROW_RIGHT)
        deadline_input.send_keys("0209")
        deadline_input.send_keys(Keys.ARROW_RIGHT)
        deadline_input.send_keys("AM")

        # --- Cliquer sur submit ---
        submit_btn = modal.find_element(By.XPATH, "//button[@type='submit']")
        driver.execute_script("arguments[0].click();", submit_btn)

        # --- Attendre que la modal disparaisse ---
        WebDriverWait(driver, 10).until(EC.invisibility_of_element(modal))

        # --- Vérifier que le survey a été créé ---
        survey_row = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, f"//tbody//tr[.//div[text()='{title}']]"
            ))
        )
        assert survey_row is not None

    # --- Créer plusieurs surveys ---
    surveys_to_create = [
        ("Sondage All-in-One Selenium", "ALL_IN_ONE_PAGE"),
        ("Sondage One-by-One Selenium", "ONE_BY_ONE_PAGE"),
        ("Sondage Recherche 1", "ALL_IN_ONE_PAGE"),
        ("Sondage Recherche 2", "ONE_BY_ONE_PAGE"),
        ("Sondage Recherche 3", "ALL_IN_ONE_PAGE")
    ]

    for title, response_type in surveys_to_create:
        create_survey(title, response_type)

    # --- Tester la barre de recherche ---
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//input[@placeholder='Search surveys by title or description...']"
        ))
    )
    search_input.send_keys("Recherche 2")
    time.sleep(1)

    # Vérifier que le survey correspondant apparaît
    result_row = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH, "//tbody//tr[.//div[text()='Sondage Recherche 2']]"
        ))
    )
    assert result_row is not None