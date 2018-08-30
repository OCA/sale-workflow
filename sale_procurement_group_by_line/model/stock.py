# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _default_sale_line_id(self):
        line = self.env['sale.order.line'].search(
            [('procurement_group_id', '=', self.id)], order='id ASC', limit=1)
        return line

    sale_line_id = fields.Many2one(
        'sale.order.line', 'Sale Order Line',
        default=_default_sale_line_id,
    )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_id = fields.Many2one(related="group_id.sale_line_id.order_id")
