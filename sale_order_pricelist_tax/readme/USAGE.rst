- for all excluded taxes select the matching included taxe
- set exclude or included tax on the pricelist
- encode a sale with the configured pricelist

Warning:
It's possible to have pricelist that depend on other pricelist.
Just keep in mind that there is no magic that will convert tax included/excluded

So if you create a tax excluded pricelist base on a tax included pricelist it will use
the raw amount (tax included) of the tax included pricelist.
There is no plan to add any logic of removing the tax amount (too complex, and maybe useless).
