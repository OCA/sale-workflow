# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_cashondelivery = fields.Float(
        string='Total cashondelivery',
        related='sale_id.total_cashondelivery',
        store=False
    )
