# Copyright 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        values = super()._get_new_picking_values()
        # v19 migration: group_id was removed in Odoo 19, so we link via
        # sale_line_id.order_id instead
        sale = self.sale_line_id.order_id[:1]
        if sale:
            values["workflow_process_id"] = sale.workflow_process_id.id
        return values
