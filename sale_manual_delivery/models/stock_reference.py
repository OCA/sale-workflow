# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2021 Iván Todorovich, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockReference(models.Model):
    _inherit = "stock.reference"

    partner_id = fields.Many2one("res.partner")
    date_planned = fields.Date()
