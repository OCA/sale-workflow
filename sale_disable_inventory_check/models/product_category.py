# Copyright Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    check_stock_on_sale = fields.Boolean(
        company_dependent=True,
        help="Uncheck if you want to disable warning 'Not enough inventory'"
             " when there isn't enough product in stock",
        string="Check Stock on Sale",
        default=True
    )
