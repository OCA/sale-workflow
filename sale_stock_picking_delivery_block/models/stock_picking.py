# Copyright 2022 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    block_delivery = fields.Boolean(related="sale_id.block_delivery")
    sale_state = fields.Selection(related="sale_id.state")
