"""Build deck.html, a standalone copy of the pedagogy deck for offline viewing.

The slide files in slides/ and deck.css are the source of truth. They are the
same files published to the Slides artifact on claude.ai. Run from the
repository root:

    python docs/slides/pedagogy-deck/build_standalone.py

deck.html opens in presentation mode: one slide at a time, scaled to the window.
Left arrow, Space or a click goes to the next slide (the deck reads right to
left), Right arrow goes back, F toggles full screen, and G toggles a scrolling
view of all slides.
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
@media (max-width: 1960px) { body:not(.present) { zoom: 0.5 } }
body.present { background: #0B1222; display: block; padding: 0; height: 100vh; overflow: hidden; cursor: pointer; }
body.present > section { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) scale(var(--s, 0.5)); }
body.present > section:not(.active) { display: none !important; }
#counter { position: fixed; left: 16px; bottom: 12px; font: 600 16px/1 Heebo, Arial, sans-serif; color: #C9D3E3; background: rgba(11, 18, 34, .7); padding: 6px 12px; border-radius: 999px; direction: ltr; }
body:not(.present) #counter { display: none; }
"""

PRESENT_JS = """
(() => {
  const slides = [...document.querySelectorAll('body > section')];
  const counter = document.getElementById('counter');
  let i = Math.min(Math.max(parseInt((location.hash.match(/slide-(\\d+)/) || [])[1] || '1', 10) - 1, 0), slides.length - 1);
  const fit = () => document.body.style.setProperty('--s', Math.min(innerWidth / 1920, innerHeight / 1080));
  const show = n => {
    i = Math.min(Math.max(n, 0), slides.length - 1);
    slides.forEach((s, k) => s.classList.toggle('active', k === i));
    counter.textContent = `${i + 1} / ${slides.length}`;
    history.replaceState(null, '', `#slide-${i + 1}`);
  };
  document.body.classList.add('present');
  fit(); show(i);
  addEventListener('resize', fit);
  addEventListener('keydown', e => {
    if (['ArrowLeft', 'ArrowDown', 'PageDown', ' ', 'Enter'].includes(e.key)) { e.preventDefault(); show(i + 1); }
    else if (['ArrowRight', 'ArrowUp', 'PageUp', 'Backspace'].includes(e.key)) { e.preventDefault(); show(i - 1); }
    else if (e.key === 'Home') show(0);
    else if (e.key === 'End') show(slides.length - 1);
    else if (e.key === 'f' || e.key === 'F') { document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); }
    else if (e.key === 'g' || e.key === 'G') { document.body.classList.toggle('present'); }
  });
  addEventListener('click', () => { if (document.body.classList.contains('present')) show(i + 1); });
})();
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
        "</head>\n<body>\n" + "\n".join(slides)
        + f"\n<div id=\"counter\"></div>\n<script>{PRESENT_JS}</script>\n</body>\n</html>\n"
    )
    (HERE / "deck.html").write_text(html, encoding="utf-8", newline="\n")
    print(f"Wrote {HERE / 'deck.html'} with {len(slides)} slides")


if __name__ == "__main__":
    main()
