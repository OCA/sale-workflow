To use this module, you need to configure a product with packaging:

1.  Go to *Sales \> Products \> Products* and select or create a
    product.
2.  In the *Inventory* tab, add some packaging(s).
3.  Enable *Sales* and in one packaging.
4.  Sort the packaging options at will. The first one enabled for *Sales* will
    be considered the default one.

Then you have to sell it:

1.  Go to *Sales \> Orders \> Quotations* and create a new quotation.
2.  Select any customer.
3.  Select that product.

You will notice that:
- The product is added with the default sale packaging.
- The packaging quantity is set to 1 packaging unit.
- The product UoM quantity is set to the amount of units contained in 1 packaging.
- When changing to another product, instead of keeping the amount of UoM units,
  we now keep the packaging qty, and the UoM qty is recomputed accordingly.
