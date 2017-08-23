# coding: utf-8
# © 2015 Akretion, Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    option_ids = fields.Many2many(
        comodel_name='sale.order.line.option',
        relation='option_lot_rel', column1='lot_id', column2='option_id',
        string='Option lines')
