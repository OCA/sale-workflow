# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_catalog_line_quantity_vals(self, product, quantity, line=False):
        """Express the catalog quantity in the secondary unit the card shows:
        the one of the line (see ``sale.order.line._get_product_catalog_lines_data``
        in ``sale_order_secondary_unit``), or the product default sale secondary
        unit for a new line, as ``_update_order_line_info`` does there.
        """
        vals = super()._get_catalog_line_quantity_vals(product, quantity, line=line)
        secondary_uom = line.secondary_uom_id if line else product.sale_secondary_uom_id
        if not secondary_uom:
            return vals
        vals = {"secondary_uom_id": secondary_uom.id, "secondary_uom_qty": quantity}
        if line:
            # Both quantities in the same write, as sale_stock_secondary_unit
            # sizes the procurement delta from them.
            vals["product_uom_qty"] = line._secondary_qty_to_product_qty(
                secondary_uom, quantity
            )
        elif secondary_uom.dependency_type != "independent":
            vals["product_uom_qty"] = product.uom_id._compute_quantity(
                quantity * secondary_uom.factor, product.uom_id
            )
        return vals
