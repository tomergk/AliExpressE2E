# Future Improvements

## Architecture Refactor
Split each page into two files following the Model-Controller convention:
- `*Model.py` — locators only
- `*Controller.py` — actions only

## Popup Handling
Replace proactive `close_popup()` calls after every navigation with a reactive approach:
- If an action fails, attempt `close_popup()` and retry
- Similar to the existing `_handle_bot_detection` fallback pattern in `base_page.py`

## BasePage Utility
Add `wait_and_click(selector)` method to `BasePage` that combines `wait_for_element` + `click` into one call.
Keep the two separate methods as well — sometimes you only want to wait without clicking.

## Smarter Add-to-Cart Wait
In `product_page.py` `add_to_cart()`, replace the fixed `wait_for_timeout(1500)` with a smart wait:
check that the cart counter in the navbar has incremented instead of sleeping a fixed time.
