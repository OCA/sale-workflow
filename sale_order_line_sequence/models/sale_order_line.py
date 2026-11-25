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

    # Do not depend on "sequence": the web client would send one onchange per
    # line when lines are reordered by drag and drop, flooding the server on
    # large orders. The line numbers are recomputed in write() instead.
    @api.depends("order_id.order_line")
    def _compute_visible_sequence(self):
        for so in self.mapped("order_id"):
            sequence = 1
            order_lines = so.order_line.filtered(
                lambda order_line: not order_line.display_type
            )
            for line in sorted(order_lines, key=lambda order_line: order_line.sequence):
                line.visible_sequence = sequence
                sequence += 1

    def write(self, vals):
        res = super().write(vals)
        if "sequence" in vals:
            self.env.add_to_compute(
                self._fields["visible_sequence"], self.order_id.order_line
            )
        return res
