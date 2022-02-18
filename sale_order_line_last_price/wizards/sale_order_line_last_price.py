# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2022 Xtendoo - Daniel Domínguez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLinePriceHistory(models.TransientModel):
    _inherit = "sale.order.line.price.history"

    @api.onchange("include_quotations")
    def _onchange_partner_id(self):
        self.line_ids = False
        states = ["sale", "done"]
        if self.include_quotations:
            states += ["draft", "sent"]
        domain = [
            ("product_id", "=", self.product_id.id),
            ("state", "in", states),
        ]
        vals = []
        order_lines = self.env["sale.order.line"].search(
            domain, order="create_date desc", limit=20
        )
        order_lines -= self.sale_order_line_id
        for order_line in order_lines:
            vals.append(
                (
                    0,
                    False,
                    {
                        "sale_order_line_id": order_line.id,
                        "history_sale_order_line_id": self.sale_order_line_id.id,
                    },
                )
            )
        self.line_ids = vals
