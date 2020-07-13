# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_packagings_with_multiple_qty(self, qty):
        packagings = super()._get_packagings_with_multiple_qty(qty)
        return packagings.filtered(lambda pack: pack.can_be_sold)
