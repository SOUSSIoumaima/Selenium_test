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
    
    close_btn = WebDriverWait(driver, 10).until(
         EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close modal']"))
    )
    driver.execute_script("arguments[0].click();", close_btn)
    time.sleep(0.5)

    # Attendre que toutes les questions soient visibles dans le survey
    questions_elements = driver.find_elements(By.XPATH, "//p[starts-with(text(),'Question :')]")

    # Récupérer le texte de chaque question
    questions_texts = [q.text.replace("Question : ", "") for q in questions_elements]

    # Vérifier qu'au moins une question est présente
    assert len(questions_texts) > 0, "Aucune question n'a été ajoutée au survey"

    # Optionnel : afficher les questions pour debug
    print("Questions présentes dans le survey :", questions_texts)

    # --- Cliquer sur le bouton "Create New Question" ---
    create_question_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[normalize-space(text())='Create New Question']"
        ))
    )
    create_question_btn.click()

    # attendre que le modal ou la page de création de question apparaisse
    new_question_modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))  
    )
    # --- Remplir le formulaire Free Text ---
    new_question_modal.find_element(By.NAME, "subject").send_keys("test create question and add it to a survey ")
    new_question_modal.find_element(By.NAME, "questionText").send_keys("is it created ?")

    # --- Sélectionner le type FREE_TEXT ---
    select_type = new_question_modal.find_element(By.NAME, "questionType")
    select_type.send_keys("FREE_TEXT")

    # --- Soumettre le formulaire ---
    new_question_modal.find_element(By.XPATH, "//button[@type='submit']").click()

    # --- Attendre que le modal soit visible après création (au cas où) ---
    close_new_question_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[@aria-label='Close modal']"
        ))
    )
    driver.execute_script("arguments[0].click();", close_new_question_btn)

    # Après avoir fermé le modal de création, le modal de la liste des questions est toujours ouvert
    questions_modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixed"))  # ton modal principal
    )

    created_question_text = "is it created ?"

    # Attendre que la question apparaisse dans le modal
    created_question_element = WebDriverWait(questions_modal, 10).until(
        lambda m: next(
            (q for q in m.find_elements(By.XPATH, ".//p[starts-with(text(),'Question :')]")
             if created_question_text in q.text),
            None
        )
    )

    assert created_question_element is not None, "La question n'apparaît pas dans le modal"
    # --- Trouver le container de la question dans le modal ---
    created_question_container = created_question_element.find_element(By.XPATH, "./parent::div")

    # --- Cliquer sur Remove ---
    trash_btn = created_question_container.find_element(By.XPATH, ".//button[@title='Remove question']")
    driver.execute_script("arguments[0].click();", trash_btn)

    # --- Attendre que le modal de confirmation apparaisse ---
    confirm_modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//div[contains(@class,'fixed')]//h3[text()='Remove Question from Survey']/ancestor::div[contains(@class,'bg-white')]"
        ))
    )

    # --- Attendre que le bouton Delete Question soit cliquable ---
    confirm_btn = WebDriverWait(confirm_modal, 5).until(
        EC.element_to_be_clickable((
            By.XPATH,
            # Cible le bouton rouge avec texte "Delete Question" même avec le SVG à l'intérieur
            ".//button[contains(@class, 'bg-gradient-to-r') and contains(., 'Delete Question')]"
        ))
    )

    # --- Cliquer sur Delete Question via JS pour éviter problèmes de overlay ---
    driver.execute_script("arguments[0].click();", confirm_btn)

    # --- Attendre que le modal disparaisse ---
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((
            By.XPATH,
            "//div[contains(@class,'fixed')]//h3[text()='Remove Question from Survey']/ancestor::div[contains(@class,'bg-white')]"
        ))
    )
    # --- Attendre que le modal principal soit toujours présent et vérifier que la question n'y est plus ---
    questions_modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "px-6"))  # classe du modal principal
    )

    # Vérifier que la question supprimée n'existe plus dans le modal
    questions_texts_after = [q.text.replace("Question : ", "") 
                             for q in questions_modal.find_elements(By.XPATH, ".//p[starts-with(text(),'Question :')]")]

    assert created_question_text not in questions_texts_after, "La question n'a pas été supprimée du survey"

