# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import config


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    quantity_skip = fields.Boolean(default=False)

    def _onchange_eval(self, field_name, onchange, result):
        """If only product quantity is changed, we need to set
        field quantity_skip to True. This is done to avoid
        computing price unit every time when product quantity
        is changed.
        """

        ctx = self.env.context
        if field_name in ("product_uom_qty", "product_uom") and (
            not config["test_enable"]
            or (config["test_enable"] and ctx.get("prevent_onchange_quantity", False))
        ):
            self.quantity_skip = True
        return super()._onchange_eval(field_name, onchange, result)

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_price_unit(self):
        for line in self:
            if line.quantity_skip:
                line.quantity_skip = False
                continue
            # Run default computing method
            return super(SaleOrderLine, line)._compute_price_unit()
