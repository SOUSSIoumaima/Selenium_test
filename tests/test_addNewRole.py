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

@pytest.mark.order(12)
def test_add_new_Role(driver):
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

    # --- Aller dans Role and permession---
    role_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Roles & Permissions']]"))
    )
    role_btn.click()
    time.sleep(1)
    # --- Cliquer sur le bouton "Add Role" ---
    add_role_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Add Role']"))
    )
    driver.execute_script("arguments[0].click();", add_role_btn)

    # --- Attendre que le modal apparaisse ---
    add_role_modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))  # ou la classe exacte de ton modal
    )

    # --- Remplir le champ "Role Name" ---
    role_name_input = add_role_modal.find_element(By.ID, "roleName")
    role_name_input.send_keys("Selenium Role")

    # --- Remplir le champ "Role Description" ---
    role_desc_input = add_role_modal.find_element(By.ID, "roleDescription")
    role_desc_input.send_keys("Role created via Selenium automation")

    # --- Liste des permissions à cocher ---
    permissions_to_check = [
        "PERMISSION_READ",
        "ROLE_READ",
        "USER_READ",
        "SURVEY_READ",
        "OPTION_READ",
        "QUESTION_READ",
        "ORGANIZATION_READ",
        "DEPARTMENT_READ",
        "TEAM_READ"
    ]

    for perm in permissions_to_check:
        try:
            # trouver l'input par sa value
            checkbox = add_role_modal.find_element(By.XPATH, f".//input[@value='{perm}']")
            # trouver le parent label cliquable
            label = checkbox.find_element(By.XPATH, "./ancestor::label")
            # faire un vrai clic via ActionChains
            ActionChains(driver).move_to_element(label).click().perform()
            time.sleep(0.2)
        except Exception as e:
            print(f"Permission {perm} non trouvée : {e}")

        
    # --- Cliquer sur le bouton Create Role ---
    create_role_btn = add_role_modal.find_element(
        By.XPATH, ".//button[normalize-space(text())='Create Role']"
    )
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", create_role_btn)

    time.sleep(3)


