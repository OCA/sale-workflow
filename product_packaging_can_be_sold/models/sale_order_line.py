# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _can_be_sold_error_condition(self):
        self.ensure_one()
        return self.product_packaging and not self.product_packaging.can_be_sold

    @api.constrains("product_packaging", "product_packaging.can_be_sold")
    def _check_product_packaging_can_be_sold(self):
        for line in self:
            if line._can_be_sold_error_condition():
                raise ValidationError(
                    _(
                        "Packaging %s on product %s must be set as 'Can be sold'"
                        " in order to be used on a sale order."
                    )
                    % (line.product_packaging.name, line.product_id.name)
                )

    @api.onchange("product_packaging")
    def _onchange_product_packaging(self):
        if self._can_be_sold_error_condition():
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _(
                        "This product packaging must be set as 'Can be sold' in"
                        " order to be used on a sale order."
                    ),
                },
            }
        return super()._onchange_product_packaging()
