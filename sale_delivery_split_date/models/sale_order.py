# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import format_date


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        vals = super(SaleOrder, self)._prepare_procurement_group_by_line(line)
        if line._get_procurement_group_key()[0] == 24:
            if line.commitment_date:
                vals['name'] += '/' + format_date(line.env, line.commitment_date.date())
        return vals
