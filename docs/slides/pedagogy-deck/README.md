# ClearPath AI pedagogy deck

A five-slide Hebrew deck about the project's teaching and assessment design:

1. Project cover: a short description and an illustration of the green wave in Manhattan.
2. The teacher guide.
3. The graduate profile and the program rubric.
4. The work templates.
5. How the [T model](../../T-model-STEM-final-project.pdf) is implemented in ClearPath AI.

The content comes from [TeacherAndStudentguidance](../../../TeacherAndStudentguidance/README.md).

## Files

| File | What it is |
| --- | --- |
| `deck.json` | The deck index: title, slide order, sections, fonts |
| `deck.css` | Styles shared by all slides |
| `slides/*.html` | One `<section>` per slide, with speaker notes in `<aside>` |
| `build_standalone.py` | Builds `deck.html` from the files above |
| `deck.html` | Standalone copy for offline viewing in a browser (generated) |

These files are the source of truth. The same files are published to the [Slides artifact on claude.ai](https://claude.ai/artifact/3L7NETeH58eRGv3aj2tF8r), where each one is served under `project/`: for example, `slides/intro.html` becomes `project/slides/intro.html`. Change the files here, publish them to the artifact, then rebuild `deck.html`:

```powershell
python docs/slides/pedagogy-deck/build_standalone.py
```

## Right-to-left

The Slides format drops CSS `direction: rtl`, so the deck makes right-to-left explicit. Text is right-aligned and wrapped in Unicode right-to-left embedding marks (`&#8235;` … `&#8236;`). Rows and grids list their children from right to left in source order.
