# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("order_line")
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in sale order lines.
        Then we add 1 to this value for the next sequence.
        This value is given to the context of the o2m field in the view.
        So when we create new sale order lines, the sequence is automatically
        added as :  max_sequence + 1
        """
        for sale in self:
            sale.max_line_sequence = max(sale.mapped("order_line.sequence") or [0]) + 1

    max_line_sequence = fields.Integer(
        string="Max sequence in lines", compute="_compute_max_line_sequence", store=True
    )

    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line:
                line.sequence = current_sequence
                current_sequence += 1

    def write(self, line_values):
        res = super(SaleOrder, self).write(line_values)
        self._reset_sequence()
        return res

    def copy(self, default=None):
        return super(SaleOrder, self.with_context(keep_line_sequence=True)).copy(
            default
        )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # re-defines the field to change the default
    sequence = fields.Integer(
        help="Gives the sequence of this line when displaying the sale order.",
        default=9999,
        string="Sequence",
    )

    # displays sequence on the order line
    sequence2 = fields.Integer(
        help="Shows the sequence of this line in the sale order.",
        related="sequence",
        string="Line Number",
        readonly=True,
        store=True,
    )

    @api.model
    def create(self, values):
        line = super(SaleOrderLine, self).create(values)
        # We do not reset the sequence if we are copying a complete sale order
        if self.env.context.get("keep_line_sequence"):
            line.order_id._reset_sequence()
        return line
