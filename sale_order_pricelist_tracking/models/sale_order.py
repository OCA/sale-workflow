# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pricelist_id = fields.Many2one(tracking=True)
