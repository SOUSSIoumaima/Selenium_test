import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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



@pytest.mark.order(1)
def test_full_signup_flow(driver):
    driver.get("http://localhost:3000/")
    
    # Cliquer sur "Sign up here"
    signup_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign up here')]"))
    )
    signup_button.click()
    
    # Organisation Setup
    org_name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "name"))
    )
    org_name_input.send_keys("HORIZON")
    
    continue_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue To Account Creation')]")
    continue_button.click()
    
    # Signup Form
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")
    confirm_input = driver.find_element(By.NAME, "confirmPassword")
    
    username_input.send_keys("oumaima")
    email_input.send_keys("oumaima@gmail.com")
    password_input.send_keys("oumaima")
    confirm_input.send_keys("oumaima")
    
    sign_up_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign Up')]")
    sign_up_button.click()
    
    # Attendre la redirection vers le dashboard (par URL)
    WebDriverWait(driver, 15).until(lambda d: "/dashboard" in d.current_url)
    assert "/dashboard" in driver.current_url

    # Optionnel : vérifier qu'un élément unique du dashboard est affiché
    dashboard_header = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h1[text()='Dashboard']"))
    )
    assert dashboard_header.is_displayed()

@pytest.mark.order(2)    
def test_existing_organization_error(driver):
    driver.get("http://localhost:3000/")

    # Cliquer sur "Sign up here"
    signup_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign up here')]"))
    )
    signup_button.click()

    # Organisation Setup avec un nom qui existe déjà
    org_name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "name"))
    )
    org_name_input.send_keys("HORIZON")  # nom déjà existant

    continue_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue To Account Creation')]")
    continue_button.click()

    # Vérifier que l'erreur s'affiche
    error_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'bg-red-100')]")
        )
    )
    assert "An organization with the name 'HORIZON' already exists." in error_message.text


# ------------------------------
# Fonction utilitaire
# ------------------------------
def get_invite_code(driver):
    driver.get("http://localhost:3000/")

    # Connexion admin
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email_input.send_keys("oumaima@gmail.com")

    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys("oumaima")

    driver.find_element(By.XPATH, "//button[text()='Sign In']").click()

    # Attendre que le dashboard soit chargé
    WebDriverWait(driver, 10).until(lambda d: "/dashboard" in d.current_url)

    # Cliquer sur l'onglet Organization
    org_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.='Organization']"))
    )
    org_tab.click()

    # Récupérer l'élément contenant le code d’invitation
    org_code_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//code[contains(., 'Invitation Code:')]")
        )
    )

    # Extraire uniquement le code (UUID)
    text = org_code_element.text.strip()
    invite_code = text.split("Invitation Code:")[-1].strip()
    print(f"Invite code récupéré : {invite_code}")

    # 🔹 Sign Out automatique
    avatar_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//p[contains(text(),'oumaima@gmail.com')]]")
        )
    )
    avatar_button.click()

    signout_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[text()='Sign Out']]")
        )
    )
    signout_button.click()

    # Retourner le code pour l'utiliser dans le test signup
    return invite_code

@pytest.mark.order(4)
def test_signup_existing_org_flow(driver):
    # Récupérer le code d'invitation via le helper
    invite_code = get_invite_code(driver)
    
    # Aller sur la page d'accueil et cliquer sur "Sign up here"
    driver.get("http://localhost:3000/")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign up here')]"))
    ).click()

    # Cliquer sur "Sign up here" dans OrganizationSetup (join existing org)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign up here')]"))
    ).click()

    # Attendre que le formulaire soit complètement visible
    form = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.TAG_NAME, "form"))
    )

    # Récupérer tous les champs depuis le formulaire
    username_input = form.find_element(By.NAME, "username")
    email_input = form.find_element(By.NAME, "email")
    invite_input = form.find_element(By.NAME, "inviteCode")
    password_input = form.find_element(By.NAME, "password")
    confirm_input = form.find_element(By.NAME, "confirmPassword")

    # Remplir le formulaire
    username_input.send_keys("med yassin")
    email_input.send_keys("med.yassin@gmail.com")
    invite_input.send_keys(invite_code)
    password_input.send_keys("medyassin")
    confirm_input.send_keys("medyassin")

    # Soumettre le formulaire
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Join Organization']"))
    ).click()

    WebDriverWait(driver, 10).until(lambda d: "/user-home" in d.current_url)
