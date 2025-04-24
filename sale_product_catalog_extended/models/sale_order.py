# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_catalog_order_line_filter_domain(self, product_id, **kwargs):
        """Get the domain used to filter lines from catalog."""
        return [("product_id", "=", product_id)]

    def _get_catalog_order_line(self, product_id, **kwargs):
        """Return the ids of the catalog order lines to be able to open
        them from catalog.
        """
        self.ensure_one()
        return self.order_line.filtered_domain(
            self._get_catalog_order_line_filter_domain(product_id, **kwargs)
        ).ids


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_product_catalog_lines_data(self, **kwargs):
        res = super()._get_product_catalog_lines_data(**kwargs)
        if len(self) > 1:
            res["readOnly"] = (
                self.order_id._is_readonly()
                or self.product_id.sale_line_warn == "block"
                or any(self.mapped(lambda sol: bool(sol.combo_item_id)))
            )
            res["multiLine"] = True
        return res
