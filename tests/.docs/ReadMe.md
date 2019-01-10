Introduction
============

# Docs

Cd into the parent dir of ``Readme``.

The doc gneration build is served by ``pip install test_requirements.txt``

cd int ``docs/`` where the conf.py is situated

_maybe:
```sphinx-apidoc -f -d 4 --implicit-namespaces -o .docs ..```

```sphinx-build .docs ../tests/.docs/html```


# API

Make sure you have sphinx installed ``pip install sphinx``.
Inside the `/gen` folder, run ``sphinx-apidoc -f -o . ../`` to create the .rst source.
Generate the documentation ``make html``.

A reStructuredText document is simply a plain text file
with some markup to specify the format or the semantics of the text.

There are two types of markup:

*  inline markup: for example, ``*the surrounding asterisks would mark
   this text as italics*``, like *this*.

*  explicit markup: is used for text that need special handling,
   such as footnotes, tables, or generic directives.
   Explicit markup blocks always start with ``..`` followed by whitespace.