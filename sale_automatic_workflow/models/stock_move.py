# -*- coding: utf-8 -*-
# © 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# © 2013 Camptocamp SA (author: Guewen Baconnier)
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_new_picking_values(self):
        values = super(StockMove, self)._get_new_picking_values()
        if self.procurement_id.sale_line_id:
            sale = self.procurement_id.sale_line_id.order_id
            values['workflow_process_id'] = sale.workflow_process_id.id
        return values
