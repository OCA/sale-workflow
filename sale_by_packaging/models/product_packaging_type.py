# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductPackagingType(models.Model):
    _inherit = "product.packaging.type"

    can_be_sold = fields.Boolean(string="Can be sold", default=True,)
