"""Rehearse the Tel Aviv clicks against a disposable local simulator."""

import argparse
import os

from playwright.sync_api import expect, sync_playwright


def unlock(page):
    access = page.get_by_label("Presenter access")
    expect(page.locator("#presenter-token:visible, #reset:enabled").first).to_be_visible()
    if access.is_visible():
        access.fill(os.environ["CLEARPATH_CONTROL_TOKEN"])
        page.get_by_role("button", name="Unlock").click()
    expect(page.get_by_role("button", name="Reset", exact=True)).to_be_enabled()


def check_dispatch(page, base):
    page.goto(f"{base}/simulator/tel-aviv")
    page.get_by_role("link", name="Tel Aviv dispatch").click()
    expect(page.get_by_role("heading", name="Rescue fleet")).to_be_visible()
    rows = page.locator("#fleet-units li")
    for place in ("פנקס", "ז׳בוטינסקי", "בן יהודה", "נחמני", "דרך יפו", "ספורטק"):
        expect(rows.filter(has_text=place)).to_have_count(1)
    unlock(page)
    reset = page.get_by_role("button", name="Reset", exact=True)
    try:
        reset.click()
        expect(page.locator("#route-status")).to_have_text("Waiting for an approved dispatch.")
        page.get_by_label("Playback speed").select_option("8")
        page.locator("#density").focus()
        page.keyboard.press("Home")
        page.get_by_label("What happened?").fill("אירוע רפואי בדרך יפו. נדרש אמבולנס.")
        page.get_by_label("Incident location", exact=True).select_option("Jaffa Road")
        page.get_by_role("button", name="Propose dispatch").click()
        expect(page.get_by_label("Vehicle · estimated drive time")).to_have_value("ambulance-2")
        expect(page.locator("#fleet-count")).to_have_text("6 available")
        page.get_by_role("button", name="Approve dispatch").click()
        expect(rows.filter(has_text="Ambulance 2")).to_contain_text("Dispatched")
        expect(page.locator("#fleet-trip")).to_contain_text("en route to Jaffa Road")
        prefix = f"{base}/simulation/tel-aviv-dispatch/state"
        state = page.request.get(prefix).json()
        unit = next(unit for unit in state["fleet"] if unit["id"] == "ambulance-2")
        assert state["route"] and state["origin"] == unit["point"] and state["dispatch_destination"] == "Jaffa Road"
        expect(page.locator("#fleet-trip")).to_contain_text("is available again", timeout=60_000)
        expect(page.locator("#fleet-count")).to_have_text("6 available")
    finally:
        reset.click()
        expect(page.locator("#route-status")).to_have_text("Waiting for an approved dispatch.")
    print("Verified fleet visibility, Hebrew report review, approval, Tel Aviv routing, arrival, and availability.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--channel", choices=("chrome", "msedge"), help="Use an installed browser.")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--dispatch", action="store_true", help="Rehearse the Tel Aviv dispatcher workflow.")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel=args.channel, headless=not args.headed, args=["--enable-unsafe-swiftshader"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        if args.dispatch:
            check_dispatch(page, base)
            return
        page.goto(f"{base}/simulator")
        manhattan = page.request.get(f"{base}/simulation/state").json()
        page.get_by_role("link", name="Tel Aviv", exact=True).click()
        expect(page.get_by_role("heading", level=1)).to_contain_text("Tel Aviv")
        expect(page.get_by_text("כיכר הבימה", exact=True)).to_be_visible()
        reset = page.get_by_role("button", name="Reset", exact=True)
        unlock(page)
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
