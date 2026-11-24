"""Rehearse the Tel Aviv clicks against a disposable local simulator."""

import argparse
import os

from playwright.sync_api import expect, sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--channel", choices=("chrome", "msedge"), help="Use an installed browser.")
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel=args.channel, headless=not args.headed, args=["--enable-unsafe-swiftshader"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"{base}/simulator")
        manhattan = page.request.get(f"{base}/simulation/state").json()
        page.get_by_role("link", name="Tel Aviv").click()
        expect(page.get_by_role("heading", level=1)).to_contain_text("Tel Aviv")
        expect(page.get_by_text("כיכר הבימה", exact=True)).to_be_visible()
        reset = page.get_by_role("button", name="Reset", exact=True)
        access = page.get_by_label("Presenter access")
        expect(page.locator("#presenter-token:visible, #reset:enabled").first).to_be_visible()
        if access.is_visible():
            access.fill(os.environ["CLEARPATH_CONTROL_TOKEN"])
            page.get_by_role("button", name="Unlock").click()
        expect(reset).to_be_enabled()
        try:
            reset.click()
            expect(page.locator("#origin-label")).to_have_text("Ichilov Hospital")
            expect(page.locator("#destination-label")).to_have_text("Rabin Square")
            for landmark in ("Dizengoff Square", "Sarona Market", "Habima Square"):
                page.get_by_label("Simulated incident location").select_option(landmark)
                page.get_by_role("button", name="Set incident").click()
                expect(page.locator("#destination-label")).to_have_text(landmark)
                state = page.request.get(f"{base}/simulation/tel-aviv/state").json()
                assert state["route_status"] == "en_route" and len(state["route"]) > 1

            page.get_by_role("button", name="Start simulation").click()
            expect(page.locator("#clock")).not_to_have_text("00:00")
            page.get_by_role("button", name="Pause").click()
            expect(page.locator("#connection-text")).to_have_text("Paused")
        finally:
            reset.click()
            expect(page.locator("#destination-label")).to_have_text("Rabin Square")
            expect(page.locator("#clock")).to_have_text("00:00")

        current_manhattan = page.request.get(f"{base}/simulation/state").json()
        assert current_manhattan["destination"] == manhattan["destination"]
        assert current_manhattan["closures"] == manhattan["closures"]
        browser.close()
    print("Verified Tel Aviv navigation, landmark selections, routes, playback, and reset in Chromium.")


if __name__ == "__main__":
    main()
