# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Field

get_depends_original = Field.get_depends


def get_depends(self, model):
    """Override of the Python method to remove the dependency of the unit fields."""
    depends, depends_context = get_depends_original(self, model)
    if model._name == "sale.order.line" and self.name in {
        "price_unit",
        "discount",
        "pricelist_item_id",
    }:
        if "product_uom_qty" in depends:
            depends.remove("product_uom_qty")
        if "product_uom" in depends:
            depends.remove("product_uom")
    return depends, depends_context


# Monkey-patching of the method
Field.get_depends = get_depends
