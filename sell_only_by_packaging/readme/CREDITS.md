The development and migration of this module has been financially supported by:

- Camptocamp
- Niboo

This module feature was extracted from the original
[sale-workflow/sale_by_packaging](https://github.com/oca/sale-workflow/tree/14.0/sale_by_packaging)
module.

The migration to 19.0 reimplements the module on top of units of measure,
as the `product.packaging` model was removed from Odoo in 19.0. The
`force_sale_qty` flag therefore moved from `product.packaging` to
`uom.uom`, and the dependency on `product_packaging_level_salable` was
dropped. Databases coming from 18.0 have to set that flag again on the
units of measure replacing their former packagings.
