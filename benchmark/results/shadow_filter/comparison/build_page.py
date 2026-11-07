"""Inline data.json into template.html and write filter_comparison.html (same folder)."""
import os

here = os.path.dirname(os.path.abspath(__file__))
data = open(os.path.join(here, "data.json"), encoding="utf-8").read()
page = open(os.path.join(here, "template.html"), encoding="utf-8").read()
assert page.count("/*DATA*/") == 1
out = os.path.join(here, "filter_comparison.html")
with open(out, "w", encoding="utf-8") as fp:
    fp.write(page.replace("/*DATA*/", data))
print("written", out, len(page) + len(data), "bytes")
