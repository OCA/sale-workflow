Usage
=====

To use this module:

1. Create one or more UoMs that represent the sales multiples you want to sell
   by (for example, *Pack of 100*).
2. On the product form, set the **Sales Multiple** field to the desired UoM.
3. In the sale order form, select the product and enter a line quantity.
4. The entered quantity is proposed **rounded UP** to the nearest valid
   multiple.

If no Sales Multiple is set on the product, no rounding is applied.

For UoMs based on *Unit(s)*, the proposed quantity is rounded up to an integer
count of the sale order line UoM. For dimensional UoMs, fractional quantities
can be proposed.
