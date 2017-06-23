# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line')
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in sale order lines.
        Then we add 1 to this value for the next sequence.
        This value is given to the context of the o2m field in the view.
        So when we create new sale order lines, the sequence is automatically
        added as :  max_sequence + 1
        """
        self.max_line_sequence = (
            max(self.mapped('order_line.sequence') or [0]) + 1)

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='_compute_max_line_sequence')

    @api.multi
    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line:
                line.write({'sequence': current_sequence})
                current_sequence += 1

    @api.multi
    def write(self, line_values):
        res = super(SaleOrder, self).write(line_values)
        for rec in self:
            rec._reset_sequence()
        return res

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        self2 = self.with_context(keep_line_sequence=True)
        return super(SaleOrder, self2).copy(default)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # re-defines the field to change the default
    sequence = fields.Integer(help="Gives the sequence of this line when "
                                   "displaying the sale order.",
                              default=9999)

    # displays sequence on the order line
    sequence2 = fields.Integer(help="Shows the sequence of this line in "
                               "the sale order.",
                               related='sequence', readonly=True,
                               store=True)

    @api.model
    def create(self, values):
        line = super(SaleOrderLine, self).create(values)
        # We do not reset the sequence if we are copying a complete sale order
        if 'keep_line_sequence' not in self.env.context:
            line.order_id._reset_sequence()
        return line

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        if 'keep_line_sequence' not in self.env.context:
            default['sequence'] = 9999
        return super(SaleOrderLine, self).copy(default)
