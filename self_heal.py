
from playwright.sync_api import sync_playwright
from pathlib import Path

# Create the screenshots folder
Path("screenshots").mkdir(exist_ok=True)

shop_url = Path("mock_shop.html").resolve().as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    try:
        page = browser.new_page(
            viewport={"width": 390, "height": 844}
        )

        page.goto(shop_url)

        button = page.get_by_role(
            "button",
            name="Proceed to Checkout"
        )

        # Measure the button before the fix
        original = button.evaluate("""
            element => {
                const rect = element.getBoundingClientRect();

                return {
                    width: rect.width,
                    right: rect.right,
                    viewportWidth: document.documentElement.clientWidth
                };
            }
        """)

        print("Before fix:", original)

        # Apply a temporary CSS fix in the browser
        button.evaluate("""
            element => {
                element.style.width = "100%";
                element.style.boxSizing = "border-box";
                element.style.maxWidth = "100%";
            }
        """)

        # Measure the button after the fix
        fixed = button.evaluate("""
            element => {
                const rect = element.getBoundingClientRect();

                return {
                    width: rect.width,
                    right: rect.right,
                    viewportWidth: document.documentElement.clientWidth
                };
            }
        """)

        print("After fix:", fixed)

        fix_successful = (
            fixed["right"] <= fixed["viewportWidth"]
        )

        # Save the screenshot while the browser is still open
        try:
            page.screenshot(
                path="screenshots/fixed_mobile.png",
                full_page=False,
                timeout=15000
            )
            print("Screenshot saved successfully.")
        except Exception as error:
            print("Screenshot failed:", error)

        if fix_successful:
            print("SELF-HEALING SUCCESS: Checkout button fits!")
        else:
            print("FIX INCOMPLETE: Checkout button still overflows.")

    finally:
        browser.close()
