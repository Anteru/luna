Luna
====

**Luna** is a tiny vector-based drawing library. It currently uses ``svgwrite`` to produce SVG output and Cairo for PNG and PDF.

License
-------

**Luna** is licensed under the two-clause BSD license. See ``LICENSE.txt`` for details.

Installation
------------

Install ``svgwrite`` and ``cairocffi`` using PIP:

    pip install svgwrite cairocffi

You can now use **Luna** by using ``import luna``. There are no further dependencies for **Luna**. The examples require ``numpy``.

General usage
-------------

The main class in Luna is ``Drawing``, which represents one drawing. Elements can be freely created and added to the drawing using ``Add``.
