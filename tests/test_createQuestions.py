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


@pytest.mark.order(8)
def test_create_questions(driver):
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

    # --- Aller dans Question Management ---
    questions_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Questions']]"))
    )
    questions_btn.click()
    time.sleep(1)

    # ----------------------------
    # 1. FREE TEXT
    # ----------------------------

    # --- Cliquer sur Create Question ---
    create_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Question')]"))
    )
    create_btn.click()

    modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))
    )

    # --- Remplir le formulaire Free Text ---
    modal.find_element(By.NAME, "subject").send_keys("Sujet Free Text")
    modal.find_element(By.NAME, "questionText").send_keys("Quelle est votre opinion ?")

    # --- Sélectionner le type FREE_TEXT ---
    select_type = modal.find_element(By.NAME, "questionType")
    select_type.send_keys("FREE_TEXT")

    # --- Soumettre le formulaire ---
    modal.find_element(By.XPATH, "//button[@type='submit']").click()
    WebDriverWait(driver, 10).until(EC.invisibility_of_element(modal))

    # --- Vérifier que la question apparaît dans la liste ---
    question_card = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'p-5') and .//p[text()='Quelle est votre opinion ?']]")
        )
    )
    assert question_card is not None

    # ----------------------------
    # 2. DATE PICKER
    # ----------------------------

    # --- Cliquer sur Create Question ---
    create_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Question')]"))
    )
    create_btn.click()

    modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))
    )

    # --- Remplir le formulaire Date Picker ---
    modal.find_element(By.NAME, "subject").send_keys("Sujet Date Picker")
    modal.find_element(By.NAME, "questionText").send_keys("Choisissez une date")

    # --- Sélectionner le type DATE_PICKER ---
    select_type = modal.find_element(By.NAME, "questionType")
    select_type.send_keys("DATE_PICKER")

    # --- Soumettre le formulaire ---
    modal.find_element(By.XPATH, "//button[@type='submit']").click()
    WebDriverWait(driver, 10).until(EC.invisibility_of_element(modal))

    # --- Vérifier que la question apparaît dans la liste ---
    question_card = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'p-5') and .//p[text()='Choisissez une date']]")
        )
    )
    assert question_card is not None

    # ----------------------------
    # 4. MULTIPLE CHOICE TEXT
    # ----------------------------
    # --- Cliquer sur Create Question ---
    create_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Question')]"))
    )
    create_btn.click()

    modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))
    )

    # --- Remplir le formulaire Multiple Choice Text ---
    modal.find_element(By.NAME, "subject").send_keys("Sujet Multiple Choice")
    modal.find_element(By.NAME, "questionText").send_keys("Quelle couleur préférez-vous ?")

    select_type = modal.find_element(By.NAME, "questionType")
    select_type.send_keys("MULTIPLE_CHOICE_TEXT")

    # --- Cliquer 3 fois sur Add option ---
    add_option_btn = modal.find_element(By.XPATH, ".//button[text()='Add option']")
    for _ in range(3):
        add_option_btn.click()
        time.sleep(0.5)  # petit délai pour que le DOM se mette à jour

    # --- Récupérer les divs contenant les options ---
    option_divs = modal.find_elements(By.XPATH, ".//div[contains(@class, 'flex space-x-4 items-center')]")

    # --- Remplir chaque option ---
    # Option 1
    inputs = option_divs[0].find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys("Rouge")  # texte
    inputs[1].clear()
    inputs[1].send_keys("2")      # score
    inputs[2].click()             # correct

    # Option 2
    inputs = option_divs[1].find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys("Bleu")
    inputs[1].clear()
    inputs[1].send_keys("2")
    inputs[2].click()             # correct

    # Option 3
    inputs = option_divs[2].find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys("Vert")
    inputs[1].clear()
    inputs[1].send_keys("0")
    # pas de clic pour correct

    # --- Soumettre le formulaire ---
    modal.find_element(By.XPATH, ".//button[text()='Submit']").click()
    WebDriverWait(driver, 10).until(EC.invisibility_of_element(modal))

    # --- Vérifier que la question apparaît dans la liste ---
    question_card = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'p-5') and .//p[text()='Quelle couleur préférez-vous ?']]")
        )
    )
    assert question_card is not None


    # ----------------------------
    # SINGLE CHOICE TEXT
    # ----------------------------

    # --- Cliquer sur Create Question ---
    create_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Question')]"))
    )
    create_btn.click()

    modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))
    )

    # --- Remplir le formulaire Single Choice Text ---
    modal.find_element(By.NAME, "subject").send_keys("Sujet Single Choice")
    modal.find_element(By.NAME, "questionText").send_keys("Quel est votre fruit préféré ?")

    select_type = modal.find_element(By.NAME, "questionType")
    select_type.send_keys("SINGLE_CHOICE_TEXT")

    # --- Cliquer 3 fois sur Add option ---
    add_option_btn = modal.find_element(By.XPATH, ".//button[text()='Add option']")
    for _ in range(3):
        add_option_btn.click()
        time.sleep(0.5)  # petit délai pour que le DOM se mette à jour

    # --- Récupérer les divs contenant les options ---
    option_divs = modal.find_elements(By.XPATH, ".//div[contains(@class, 'flex space-x-4 items-center')]")

    # --- Remplir chaque option ---
    # Option 1
    inputs = option_divs[0].find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys("Pomme")  # texte
    inputs[1].clear()
    inputs[1].send_keys("2")      # score
    inputs[2].click()             # correcte

    # Option 2
    inputs = option_divs[1].find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys("Banane")
    inputs[1].clear()
    inputs[1].send_keys("0")
    # pas de clic pour correct

    # Option 3
    inputs = option_divs[2].find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys("Orange")
    inputs[1].clear()
    inputs[1].send_keys("0")
    # pas de clic pour correct

    # --- Soumettre le formulaire ---
    modal.find_element(By.XPATH, ".//button[text()='Submit']").click()
    WebDriverWait(driver, 10).until(EC.invisibility_of_element(modal))

    # --- Vérifier que la question apparaît dans la liste ---
    question_card = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'p-5') and .//p[text()='Quel est votre fruit préféré ?']]")
        )
    )
    assert question_card is not None

    # ----------------------------
    # 5. YES/NO
    # ----------------------------

    # --- Cliquer sur Create Question ---
    create_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Question')]"))
    )
    create_btn.click()

    modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))
    )

    # --- Remplir le formulaire YES/NO ---
    modal.find_element(By.NAME, "subject").send_keys("Sujet Yes/No")
    modal.find_element(By.NAME, "questionText").send_keys("Aimez-vous le café ?")

    select_type = modal.find_element(By.NAME, "questionType")
    select_type.send_keys("YES_NO")

    # --- Cliquer 2 fois sur Add option ---
    add_option_btn = modal.find_element(By.XPATH, ".//button[text()='Add option']")
    for _ in range(2):
        add_option_btn.click()
        time.sleep(0.5)

    # --- Récupérer les divs contenant les options ---
    option_divs = modal.find_elements(By.XPATH, ".//div[contains(@class, 'flex space-x-4 items-center')]")

    # --- Option 1 : Yes ---
    inputs = option_divs[0].find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys("Yes")   # texte
    inputs[1].clear()
    inputs[1].send_keys("1")     # score
    inputs[2].click()            # correct

    # --- Option 2 : No ---
    inputs = option_divs[1].find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys("No")
    inputs[1].clear()
    inputs[1].send_keys("0")
    # pas de clic pour correct

    # --- Soumettre le formulaire ---
    modal.find_element(By.XPATH, ".//button[text()='Submit']").click()
    WebDriverWait(driver, 10).until(EC.invisibility_of_element(modal))

    # --- Vérifier que la question apparaît dans la liste ---
    question_card = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'p-5') and .//p[text()='Aimez-vous le café ?']]")
        )
    )
    assert question_card is not None

