# -*- coding: utf-8 -*-
# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        vals = super(SaleOrder, self)._prepare_procurement_group_by_line(line)
        if line._get_procurement_group_key()[0] == 24:
            if line.requested_date:
                vals['name'] += '/' + line.requested_date[:10]
        return vals
