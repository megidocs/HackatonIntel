"""Build deck.html, a standalone copy of the pedagogy deck for offline viewing.

The slide files in slides/ and deck.css are the source of truth. They are the
same files published to the Slides artifact on claude.ai. Run from the
repository root:

    python docs/slides/pedagogy-deck/build_standalone.py
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

BASE_CSS = """
* { margin: 0 }
body { background: #2b2b2b; display: flex; flex-direction: column; align-items: center; gap: 32px; padding: 32px 0; }
body > section { width: 1920px; height: 1080px; overflow: hidden; box-sizing: border-box; position: relative; flex: none; }
aside { display: none }
h1 { font-size: 96px; font-weight: 600 }
h2 { font-size: 64px; font-weight: 600 }
h3 { font-size: 44px; font-weight: 600 }
@media (max-width: 1960px) { body { zoom: 0.5 } }
"""


def main() -> None:
    deck = json.loads((HERE / "deck.json").read_text(encoding="utf-8"))
    links = sorted({face["href"] for face in deck["faces"].values() if "href" in face})
    slides = [(HERE / "slides" / f"{slide_id}.html").read_text(encoding="utf-8").strip()
              for slide_id in deck["order"]]
    head = "\n".join(f'<link rel="stylesheet" href="{href}">' for href in links)
    html = (
        "<!doctype html>\n<html lang=\"he\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{deck['title']}</title>\n{head}\n"
        f"<style>{BASE_CSS}</style>\n<style>\n{(HERE / 'deck.css').read_text(encoding='utf-8')}</style>\n"
        "</head>\n<body>\n" + "\n".join(slides) + "\n</body>\n</html>\n"
    )
    (HERE / "deck.html").write_text(html, encoding="utf-8", newline="\n")
    print(f"Wrote {HERE / 'deck.html'} with {len(slides)} slides")


if __name__ == "__main__":
    main()
