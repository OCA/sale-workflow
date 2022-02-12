# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _propagate_qty_change(self):
        lines_with_bom = self.filtered(
            lambda s: s.move_ids.bom_line_id.bom_id.type == "phantom"
        )
        lines_without_bom = self - lines_with_bom
        for line in lines_with_bom:
            bom = line.move_ids.bom_line_id.bom_id
            for bom_line, item in bom.explode(line.product_id, line.product_uom_qty)[1]:
                moves = line.move_ids.filtered(
                    lambda s: s.product_id == bom_line.product_id
                )
                moves._update_qty_recursively(item["qty"])
        super(SaleOrderLine, lines_without_bom)._propagate_qty_change()
