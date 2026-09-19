# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_product_catalog_lines_data(self, **kwargs):
        res = super()._get_product_catalog_lines_data(**kwargs)
        # For the target product, if it has a secondary unit, we need to
        #  convert quantity; if not, we'll accept the default behavior (manage
        #  the catalog with main unit), no matter if line has already second
        #  unit info
        if (
            self.product_id.sale_secondary_uom_id
            and self.product_id.sale_secondary_uom_id.dependency_type != "independent"
        ):
            if len(self) == 1:
                res["quantity"] = self.secondary_uom_qty
            elif len(self) > 1:
                # Convert each line's secondary qty to the product's default
                # secondary unit via factors (primary unit as intermediate step).
                res["quantity"] = sum(
                    line.secondary_uom_qty
                    * line.secondary_uom_id.factor
                    / line.product_id.sale_secondary_uom_id.factor
                    for line in self.filtered(lambda line: line.secondary_uom_id)
                )
        return res
