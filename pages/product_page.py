import random
from pages.base_page import BasePage


class ProductPage(BasePage):

    ADD_TO_CART_BUTTON = "button[class*='add-to-cart--addtocart']"
    VARIANT_GROUP = "div[class*='sku-item--skus']"
    VARIANT_OPTION = "div[class*='sku-item--text']:not([class*='sku-item--soldOut']), div[class*='sku-item--image']:not([class*='sku-item--soldOut'])"

    def open(self, url: str):
        self.navigate(url)
        self.close_popup()

    def select_random_variants(self):
        try:
            groups = self.page.locator(self.VARIANT_GROUP).all()
            for group in groups:
                options = group.locator(self.VARIANT_OPTION).all()
                if options:
                    random.choice(options).click()
                    self.page.wait_for_timeout(500)
        except Exception:
            pass

    def add_to_cart(self):
        self.wait_for_element(self.ADD_TO_CART_BUTTON)
        self.page.locator(self.ADD_TO_CART_BUTTON).first.click()
        self.page.wait_for_timeout(1500)
        self.close_popup()

    # Because some products are unavailable
    def can_add_to_cart(self) -> bool: 
        try:
            # If the product is out of stock / unavailable then AliExpress doesn't render the add to cart button in the DOM.
            return self.page.locator(self.ADD_TO_CART_BUTTON).first.is_visible(timeout=5000)
        except Exception:
            return False

    # Handle both new-tab and same-tab navigation back to search results
    def close_and_return_to_search(self):
        if len(self.page.context.pages) > 1:
            self.page.close()
        else:
            self.page.go_back()
