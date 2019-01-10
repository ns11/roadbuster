import os
import sys

sys.path.insert(0, os.path.abspath("../"))

extensions = ["sphinx.ext.autodoc", "pallets_sphinx_themes"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
master_doc = "index"
project = "FIL Dochub"
copyright = "Core Team, core.team@fil.com"
exclude_patterns = ["_build", ".fox"]
pygments_style = "sphinx"
html_theme = "flask"
autoclass_content = "both"
source_parsers = {".md": "recommonmark.parser.CommonMarkParser"}
