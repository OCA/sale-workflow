# Copyright 2025 APSL-Nagarro Bernat Obrador <borbador@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import models
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        self._update_negative_deliveries()
        return res

    def _update_negative_deliveries(self):
        for record in self:
            for move in record.move_lines:
                so_line = move.sale_line_id
                if (
                    so_line
                    and float_compare(
                        so_line.product_uom_qty,
                        0.0,
                        precision_rounding=so_line.product_uom.rounding,
                    )
                    < 0
                ):
                    delivered = so_line.qty_delivered or 0.0
                    so_line.qty_delivered = -(delivered + move.quantity_done)
