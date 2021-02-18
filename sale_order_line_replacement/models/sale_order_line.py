# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    replacement_line_id = fields.Many2one("sale.order.line")
    replacement_description = fields.Char()
    replaced_line_id = fields.One2many(
        "sale.order.line", inverse_name="replacement_line_id"
    )
