
from playwright.sync_api import sync_playwright
from pathlib import Path

Path("screenshots").mkdir(exist_ok=True)

shop_url = Path("mock_shop.html").resolve().as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={"width": 390, "height": 844}
    )

    page.goto(shop_url)

    # Find the checkout button
    button = page.get_by_role(
        "button",
        name="Proceed to Checkout"
    )

    # Read its position and size
    details = button.evaluate("""element => {
        const rect = element.getBoundingClientRect();

        return {
            width: rect.width,
            left: rect.left,
            right: rect.right,
            viewportWidth: document.documentElement.clientWidth
        };
    }""")

    print("Checkout button details:", details)

    test_passed = details["right"] <= details["viewportWidth"]

    if test_passed:
        print("STATUS: PASS")
        print("Checkout button fits within the viewport.")
    else:
        print("STATUS: FAIL")
        print("UI BUG FOUND: Checkout button extends beyond the viewport!")

        page.screenshot(
            path="screenshots/buggy_mobile.png",
            full_page=True
        )

    browser.close()
