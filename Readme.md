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

You can now use **Luna** by using ``import luna``. If only SVG output is required, the ``cairocffi`` module can be omitted, and vice versa for PNG & PDF output. There are no further dependencies for **Luna**. However, the examples require ``numpy``.

Design goals
------------

* Easy to use
* Efficient instancing: It should be possible to create prototype objects and distribute them in the scene
* Pure Python: It should be possible to run a pure-Python version with no external dependencies. This is particularly important for Windows.

**Luna** is designed as a declarative, object-oriented drawing system. All primitives are represented as objects and assembled into a tree. This tree is eventually processed by the backends and converted into the target format. The abstraction is modeled after common 2D drawing libraries and standards. It should be possible to provide backends in every popular 2D drawing toolkit.

General usage
-------------

The main class in Luna is ``Drawing``, which represents a drawing. Elements can be freely created and added to the drawing using ``Add``.
