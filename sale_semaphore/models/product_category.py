# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    semaphore_active = fields.Boolean()
    semaphore_discount_success = fields.Float(string="Discount Success")
    semaphore_discount_warning = fields.Float(string="Discount Warning")
    semaphore_discount_danger = fields.Float(string="Discount Danger")
