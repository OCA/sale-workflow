# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    customer_ref = fields.Char(
        string="Customer Ref.",
        help="Customer reference coming from the sale order line.",
    )
