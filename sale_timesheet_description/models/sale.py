# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        note = []
        for line in self.env['account.analytic.line'].search(
                [('so_line', '=', self.id)]):
            details = [
                line['date'],
                "%s %s" % (line.unit_amount, line.product_uom_id.name),
                line['name'],
                ]
            note.append(
                u' - '.join(map(lambda x: unicode(x) or '', details)))
        if note:
            res['name'] += "\n" + (
                "\n".join(map(lambda x: unicode(x) or '', note)))
        return res
