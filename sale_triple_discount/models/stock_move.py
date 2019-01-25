# -*- coding: utf-8 -*-
# Copyright 2019 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(StockMove, self) \
            ._get_invoice_line_vals(move, partner, inv_type)
        if inv_type in ('out_invoice', 'out_refund') \
                and move.procurement_id and move.procurement_id.sale_line_id:
            sale_line = move.procurement_id.sale_line_id
            res.update({
                'discount2': sale_line.discount2,
                'discount3': sale_line.discount3,
            })
        return res
