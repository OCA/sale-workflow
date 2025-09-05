# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def copy(self, default=None):
        archived_products = self.mapped("order_line.product_id").filtered(
            lambda p: not p.active
        )
        if archived_products:
            raise exceptions.ValidationError(
                _("You can't duplicate sale orders with archived products: {}").format(
                    ", ".join(archived_products.mapped("name"))
                )
            )
        return super().copy(default)
