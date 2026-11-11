#!/usr/bin/env python3
# Copyright (C) 2026 Hans Kristian Rosbach
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

"""Extracted, altered distribution of zanalyze for the LR3 console chart.
Original: Hans Kristian Rosbach, zlib-ng/zanalyze
Pinned source: 4cc0b3fd286c2db5ec4fdc1d2637eaab2b0ed515
Only constants and histogram functions are extracted; compression code omitted.
Functions and block constants below are unchanged from upstream lines303–305,
1671–1696. Integration and input validation belong to main.py.
"""

# histogram bar glyphs: full block tiles seamlessly; eighths give sub-cell fill
BLOCK = "\u2588"          # full block
EIGHTH = "\u258f\u258e\u258d\u258c\u258b\u258a\u2589"  # 1/8 .. 7/8 (bottom fill)

def _bar(count, max_count, width):
    """A proportional bar: full blocks + one fractional (eighth) tail cell."""
    scaled = width * count / max_count
    full = int(scaled)
    eighths = round((scaled - full) * 8)
    if eighths == 8:
        return BLOCK * (full + 1)
    if eighths:
        return BLOCK * full + EIGHTH[eighths - 1]
    return BLOCK * full


def print_histogram(title, rows, total, label_name, width=40):
    """Print a column header plus label/count/percent rows with a proportional
    bar per row. ``label_name`` names the first (label) column."""
    if not rows:
        print(f"{title}\n  (none)")
        return
    max_count = max(count for _, count in rows)
    label_width = max(len(label) for label, _ in rows)
    print(title)
    print(f"  {label_name:>{label_width}}  {'count':>10}  {'pct':>7}  distribution")
    for label, count in rows:
        bar = _bar(count, max_count, width) if count else ""
        pct = 100.0 * count / total if total else 0.0
        print(f"  {label:>{label_width}}  {count:>10}  {pct:6.2f}%  {bar}")
