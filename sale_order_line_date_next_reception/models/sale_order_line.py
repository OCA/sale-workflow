# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    next_reception_date = fields.Date(compute="_compute_next_reception_date")

    def _compute_next_reception_date(self):
        for line in self:
            line.next_reception_date = False
            qty_available = line.product_id.with_context(
                warehouse=line.order_id.warehouse_id.id
            ).qty_available
            if float_compare(
                qty_available, 0, precision_rounding=line.product_uom.rounding
            ) > 0 and line.state not in ["done", "cancel"]:
                line.next_reception_date = line.product_id.next_reception_date
