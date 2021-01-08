transpeg
=========

Wanna transparent JPEG?
Unfortunately there is no such thing except mostly unsupported JPEG 2000.
But you can convert your transparent image into SVG containing a color information as JPEG and an alpha channel as a greyscale mask.
This simple tool does exactly this.

Usage
=====

transpeg input.png output.svg

Installation
============

    pip install transpeg

Alternatives
============

1. WebP. Unfortunatelly WebP is not well supperted in Safari yet.
2. https://github.com/tannerhodges/gulp-zorrosvg
3. https://github.com/gribnoysup/jpng.svg

Why
===

1. It is dead simple in Python
2. I needed a PNG palette for a mask
