from pages.base_page import BasePage
from playwright.sync_api import expect


class LoginPage(BasePage):

    URL = "https://www.aliexpress.com"

    ACCOUNT_TRIGGER = "div[role='button'][aria-label*='account']"
    SIGNIN_BUTTON = "button[class*='my-account--signin']"
    EMAIL_INPUT = "input.cosmos-input[type='text']"
    CONTINUE_BUTTON = "button.cosmos-btn-primary.cosmos-btn-large"
    PASSWORD_INPUT = "input#fm-login-password"
    LOGIN_BUTTON = "button.cosmos-btn-primary.cosmos-btn-large.cosmos-btn-block"
    USER_AVATAR = "span[class*='user-name'], div[class*='userInfo'], a[href*='my-profile'], [class*='my-account']"

    def navigate_to_login(self):
        self.navigate(self.URL)
        self.close_popup()
        self.wait_for_element(self.ACCOUNT_TRIGGER)
        self.page.locator(self.ACCOUNT_TRIGGER).first.hover()
        self.wait_for_element(self.SIGNIN_BUTTON)
        self.page.locator(self.SIGNIN_BUTTON).first.click()

    def enter_email(self, email: str):
        self.wait_for_element(self.EMAIL_INPUT)
        self.page.fill(self.EMAIL_INPUT, email)
        expect(self.page.locator(self.EMAIL_INPUT)).to_have_value(email)
        self.page.locator("h1[role='heading']").first.click() # clicking somewhere neutral on the page to dismiss the email autocomplete dropdown

    # After entering the email, AliExpress shows a "Continue" button to proceed to the password step.
    def click_continue(self):
        self.page.locator(self.CONTINUE_BUTTON).first.click()

    def enter_password(self, password: str):
        self.wait_for_element(self.PASSWORD_INPUT)
        self.page.fill(self.PASSWORD_INPUT, password)

    def click_login_button(self):
        self.page.locator(self.LOGIN_BUTTON).first.click()
        self.page.wait_for_load_state("load")

    def is_logged_in(self) -> bool:
        try:
            self.wait_for_element(self.USER_AVATAR)
            return True
        except Exception:
            return False

    def login(self, username: str, password: str):
        self.navigate_to_login()
        self.enter_email(username)
        self.click_continue()
        self.enter_password(password)
        self.click_login_button()
        self.close_popup()
        assert self.is_logged_in(), "Login failed — check credentials or CAPTCHA"
