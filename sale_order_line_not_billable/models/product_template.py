# Copyright <2022> <Janik von Rotz - Mint System>
# Copyright <2024> <Denis Leemann - Camptocamp SA>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    billable = fields.Boolean(default=True)
