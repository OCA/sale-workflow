# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # re-defines the field to change the default
    sequence = fields.Integer(
        help="Gives the sequence of this line when displaying the sale order.",
        default=9999,
    )

    visible_sequence = fields.Integer(
        "Line Number",
        help="Displays the sequence of the line in the sale order.",
        compute="_compute_visible_sequence",
        store=True,
    )

    @api.depends("sequence", "order_id.order_line")
    def _compute_visible_sequence(self):
        for so in self.mapped("order_id"):
            sequence = 1
            order_lines = so.order_line.filtered(lambda l: not l.display_type)
            for line in sorted(order_lines, key=lambda l: l.sequence):
                line.visible_sequence = sequence
                sequence += 1
