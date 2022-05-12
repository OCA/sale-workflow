- set your product in include tax
- set exclude tax with pricelist of your choice
- encode a sale with these settings

Warning:
It's possible to have pricelist that depend on other pricelist.
Just keep in mind that there is no magic that will convert tax included/excluded

So if you create a tax excluded pricelist base on a tax included pricelist it will use
the raw amount (tax included) of the tax included pricelist.
There is no plan to add any logic of removing the tax amount (too complex, and maybe useless).
