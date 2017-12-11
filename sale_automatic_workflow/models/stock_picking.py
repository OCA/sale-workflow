# Copyright 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    workflow_process_id = fields.Many2one(
        comodel_name='sale.workflow.process',
        string='Sale Workflow Process'
    )

    @api.multi
    def validate_picking(self):
        for picking in self:
            picking.force_assign()
            self.env['stock.immediate.transfer'].create(
                {'pick_ids': [(4, picking.id)]}).process()
        return True
