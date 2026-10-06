Usage
=====

To use this module:

1. Create one or more packaging UoMs (for example, *Pack of 100*), using the
   same reference unit as the product base UoM.
2. On the product form, set the **Sales Multiple** field to the desired UoM.
3. When entering quantities on a sales order line, the quantity is
   automatically rounded **UP** to the nearest valid multiple.

If no Sales Multiple is set on the product, no rounding is applied.
