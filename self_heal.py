
from playwright.sync_api import sync_playwright
from pathlib import Path

shop_url = Path("mock_shop.html").resolve().as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={"width": 390, "height": 844}
    )

    page.goto(shop_url)

    button = page.get_by_role(
        "button",
        name="Proceed to Checkout"
    )

    # Check the original button width
    original_width = button.evaluate(
        "(element) => element.getBoundingClientRect().width"
    )

    print("Original button width:", original_width)

    # Apply a temporary CSS correction
    button.evaluate("""
        element => {
            element.style.width = "100%";
            element.style.boxSizing = "border-box";
            element.style.maxWidth = "100%";
        }
    """)

    # Verify the corrected layout
    result = page.evaluate("""
        () => ({
            pageWidth: document.documentElement.scrollWidth,
            viewportWidth: document.documentElement.clientWidth
        })
    """)

    page.screenshot(
        path="screenshots/fixed_mobile.png",
        full_page=True
    )

    print("After fix:", result)

    if result["pageWidth"] <= result["viewportWidth"]:
        print("SELF-HEALING SUCCESS: No horizontal overflow!")
    else:
        print("FIX INCOMPLETE: More investigation needed.")

    browser.close()
