from pages.base_page import BasePage
from utils.price_parser import parse_price


class SearchResultsPage(BasePage):

    SEARCH_URL = "https://www.aliexpress.com/wholesale?SearchText={query}"

    PRODUCT_CARD = "div.search-item-card-wrapper-gallery" # same for each card in the grid's list
    PRODUCT_LINK = "a.search-card-item" # different href for each
    PRICE_ELEMENT = "[aria-label*='₪'], [aria-label*='$']" # locating ₪ or $
    PRICE_SORT_BUTTON = "div[ae_object_value='price(lowest)']"
    NEXT_PAGE_BUTTON = "button.comet-pagination-item-link:has(.comet-icon-arrowleft32)"  # RTL: left arrow = next page

    def search_product(self, query: str):
        url = self.SEARCH_URL.format(query=query.replace(" ", "+"))
        self.navigate(url)
        self.close_popup()
        self.wait_for_element(self.PRODUCT_CARD)

    def sort_by_lowest_price(self):
        try:
            self.wait_for_element(self.PRICE_SORT_BUTTON)
            self.page.locator(self.PRICE_SORT_BUTTON).first.click()
            self.page.wait_for_load_state("networkidle", timeout=10000) # Playwright load state: no network activity
            self.close_popup()
        except Exception:
            pass

    def get_items_under_price(self, max_price: float, limit: int) -> list[str]:
        urls = []
        pages_visited = 0
        max_pages = 5

        while len(urls) < limit and pages_visited < max_pages:
            self.page.wait_for_load_state("load")
            cards = self.page.locator(self.PRODUCT_CARD).all()
            prev_count = len(urls)

            for card in cards:
                if len(urls) >= limit:
                    break
                try:
                    price_label = card.locator(self.PRICE_ELEMENT).first.get_attribute("aria-label", timeout=500)
                    price = parse_price(price_label)
                    if price <= max_price:
                        href = card.locator(self.PRODUCT_LINK).first.get_attribute("href")
                        if href and href not in urls:
                            urls.append(href if href.startswith("http") else "https:" + href)
                except Exception:
                    continue

            pages_visited += 1
            print(f"\n[SEARCH] Page {pages_visited}: +{len(urls) - prev_count} items (total {len(urls)}/{limit})")

            if len(urls) >= limit:
                break
            elif len(urls) == prev_count:
                break
            elif self.has_next_page():
                self.go_to_next_page()
            else:
                break

        return urls

    def detect_currency(self) -> str:
        try:
            label = self.page.locator(self.PRICE_ELEMENT).first.get_attribute("aria-label", timeout=3000) or ""
            if "₪" in label:
                return "ILS"
        except Exception:
            pass
        return "USD"

    def has_next_page(self) -> bool:
        try:
            next_btn = self.page.locator(self.NEXT_PAGE_BUTTON).first
            return next_btn.is_visible()
        except Exception:
            return False

    def go_to_next_page(self):
        self.page.locator(self.NEXT_PAGE_BUTTON).first.click()
        self.page.wait_for_load_state("load")
