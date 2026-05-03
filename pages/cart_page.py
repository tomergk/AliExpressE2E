from pages.base_page import BasePage


class CartPage(BasePage):

    CART_URL = "https://www.aliexpress.com/p/shoppingcart/index.html"

    CART_TOTAL = "div.cart-summary-item-wrapStyle-content span"
    ITEM_CHECKBOX = "span.comet-v2-checkbox-icon"
    ITEM_CHECKBOX_CHECKED = "span.comet-v2-checkbox-checked"
    POPUP_CLOSE = "button.comet-v2-drawer-close"
    DELETE_SELECTED_BTN = "div.cart-header-delete-btn"
    CONFIRM_DELETE_BTN = "button.comet-v2-btn-important"

    def open(self):
        self.navigate(self.CART_URL)
        self.close_popup()

    def select_all_items(self):
        try:
            checkboxes = self.page.locator(self.ITEM_CHECKBOX).all()
            for checkbox in checkboxes:
                if not checkbox.is_visible():
                    continue
                parent = checkbox.locator("xpath=..")
                is_checked = "checked" in (parent.get_attribute("class") or "")
                if not is_checked:
                    checkbox.click()
                    self.page.wait_for_timeout(500)
            self.page.wait_for_timeout(1000)
            popup = self.page.locator(self.POPUP_CLOSE).first
            if popup.is_visible():
                popup.click()
                self.page.wait_for_timeout(500)
        except Exception:
            pass

    def clear_cart(self):
        try:
            self.open()
            self.select_all_items()
            delete_btn = self.page.locator(self.DELETE_SELECTED_BTN).first
            if delete_btn.is_visible():
                delete_btn.click()
                self.page.wait_for_timeout(1500)
                confirm = self.page.locator(self.CONFIRM_DELETE_BTN).first
                if confirm.is_visible():
                    confirm.click()
                    self.page.wait_for_timeout(2000)
        except Exception:
            pass

    def get_total(self) -> float:
        self.wait_for_element(self.CART_TOTAL)
        total_text = self.page.locator(self.CART_TOTAL).last.inner_text()
        cleaned = "".join(c for c in total_text if c.isdigit() or c == ".")
        return float(cleaned) if cleaned else 0.0

    def assert_total_not_exceeds(self, budget_per_item: float, items_count: int):
        self.open()
        self.select_all_items()
        threshold = budget_per_item * items_count
        total = self.get_total()
        self.take_screenshot("cart_total", "screenshots/cart-screenshots")
        print(f"\n--- Cart Verification ---")
        print(f"budgetPerItem      = ₪{budget_per_item}")
        print(f"itemsCount         = {items_count}")
        print(f"budgetPerItem * itemsCount = ₪{threshold:.2f}")
        print(f"cartTotal          = ₪{total:.2f}")
        print(f"Result: {'PASS - within budget' if total <= threshold else 'FAIL - exceeds budget'}")
        print(f"-------------------------")
        assert total <= threshold, (
            f"Cart total ₪{total:.2f} exceeds budget ₪{threshold:.2f} "
            f"({items_count} items × ₪{budget_per_item})"
        )
