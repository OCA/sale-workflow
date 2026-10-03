# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _update_order_line_info(self, product_id, quantity, **kwargs):
        # Assumptions:
        # * Product will have a default sales secondary unit.
        #   If not, catalog will work with primary unit
        #   (default behavior).
        # * Even if sales line already exists,
        #   after catalog operation is finished,
        #   secondary unit is always marked as the default one,
        #   overwriting the previous selected one.
        # * If destination unit is integer (like e.g. units),
        #   rounding it is not necessary
        product = self.env["product.product"].browse(product_id)
        quantity_orig = quantity
        if (
            product.sale_secondary_uom_id
            and product.sale_secondary_uom_id.dependency_type != "independent"
        ):
            quantity = quantity * product.sale_secondary_uom_id.factor

        res = super()._update_order_line_info(product_id, quantity, **kwargs)

        if (
            product.sale_secondary_uom_id
            and product.sale_secondary_uom_id.dependency_type != "independent"
        ):
            sol = self.order_line.filtered(
                lambda line: line.product_id.id == product_id
            )
            for s in sol:
                if not s.secondary_uom_id:
                    s.write(
                        {
                            "secondary_uom_qty": quantity_orig,
                            "secondary_uom_id": product.sale_secondary_uom_id,
                        }
                    )
        return res
