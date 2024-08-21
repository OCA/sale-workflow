# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    coefficient_sale_insurance = fields.Float(
        help="coefficient which will be multiplied to the total sum of SO"
    )
    insurance_product = fields.Many2one("product.product")
