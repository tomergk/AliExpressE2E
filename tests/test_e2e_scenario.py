import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.search_results_page import SearchResultsPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage


def login(page: Page, credentials: dict):
    login_page = LoginPage(page)
    login_page.login(credentials["username"], credentials["password"])


def search_items_by_name_under_price(
    page: Page, query: str, max_price_ils: float, max_price_usd: float, limit: int = 5
) -> tuple[list[str], float]:
    search_page = SearchResultsPage(page)
    search_page.search_product(query)
    search_page.sort_by_lowest_price()
    currency = search_page.detect_currency()
    max_price = max_price_ils if currency == "ILS" else max_price_usd
    print(f"\n[CURRENCY] Detected {currency} — using max_price={max_price}")
    return search_page.get_items_under_price(max_price, limit), max_price


def add_items_to_cart(page: Page, urls: list[str]) -> int:
    added = 0
    for url in urls:
        product_page = ProductPage(page)
        product_page.open(url)
        product_page.select_random_variants()
        if not product_page.can_add_to_cart():
            product_page.close_and_return_to_search()
            continue
        product_page.add_to_cart()
        added += 1
        product_page.take_screenshot(f"item_added_{added}", BasePage.ITEMS_SCREENSHOTS)
        product_page.close_and_return_to_search()
    return added


def assert_cart_total_not_exceeds(page: Page, budget_per_item: float, items_count: int):
    cart_page = CartPage(page)
    cart_page.assert_total_not_exceeds(budget_per_item, items_count)


@allure.title("E2E Shopping Scenario — Search, Add to Cart, Verify Total")
def test_e2e_shopping_scenario(page: Page, credentials: dict, search_params: list):
    for params in search_params:
        query = params["query"]
        max_price_ils = params["max_price_ils"]
        max_price_usd = params["max_price_usd"]
        limit = params["limit"]

        with allure.step("Step 1: Login"):
            login(page, credentials)

        with allure.step(f"Step 2: Search '{query}' (ILS≤{max_price_ils} / USD≤{max_price_usd})"):
            urls, max_price = search_items_by_name_under_price(
                page, query, max_price_ils, max_price_usd, limit
            )

        with allure.step(f"Step 3: Add {len(urls)} items to cart"):
            added_count = add_items_to_cart(page, urls)

        try:
            with allure.step("Step 4: Assert cart total does not exceed budget"):
                assert added_count > 0, (
                    f"No items were added to cart — found 0 products under {max_price} "
                    f"for query '{query}'. Check price selector or budget."
                )
                assert_cart_total_not_exceeds(page, max_price, added_count)
        finally:
            with allure.step("Step 5: Clear cart for next run"):
                CartPage(page).clear_cart()
