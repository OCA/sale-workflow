Sales Product Multiple Quantity
===============================

This module adds a **Sales Multiple** unit of measure on products.

When a Sales Multiple is set, sales order line quantities entered in the sale
order form are proposed **rounded UP** to the nearest multiple of the selected
unit of measure.
This is useful for products that must be sold in fixed pack sizes
(boxes, bundles, pallets, etc.).

The rounding is performed by converting the entered quantity to the Sales
Multiple UoM, rounding the number of packs **UP**, and converting the result
back to the order line UoM.

For example, with a Sales Multiple of *Pack of 100*:
- ordering 15 packs of 5 units (75 units) is rounded to 20 packs (100 units);
- ordering 55 packs of 5 units (275 units) is rounded to 60 packs (300 units).

For UoMs that share *Unit(s)* as common reference, the proposed sale quantity is
kept as an integer count of the sale order line UoM. For dimensional UoMs, such
as kilograms or meters, fractional rounded quantities are preserved.

The rounding is intentionally limited to the sale order form. Programmatic
values written through imports, RPC calls, or custom code are not automatically
changed by this module.
