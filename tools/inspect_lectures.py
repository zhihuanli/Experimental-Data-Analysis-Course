"""Read notebook HTML in cell order for a conservative source review."""
from pathlib import Path
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def inspect(relative):
    path = ROOT / relative
    soup = BeautifulSoup(path.read_text(), "html.parser")
    cells = soup.select(".jp-Cell") or soup.select(".cell")
    print(f"PAGE {relative}")
    for i, cell in enumerate(cells):
        md = cell.select_one(".jp-RenderedMarkdown,.text_cell_render")
        code = cell.select_one(".jp-InputArea-editor,.input_area")
        if md:
            for image in md.find_all("img"):
                src = image.get("src", "")
                image.replace_with(f"[Figure: {src[:160] if not src.startswith('data:') else 'embedded image'}]")
            print(f"\nCELL {i} MARKDOWN\n{md.get_text()}")
        elif code:
            print(f"\nCELL {i} CODE\n{code.get_text().strip()}")


if __name__ == "__main__":
    for relative in sys.argv[1:]:
        inspect(relative)
