# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    def map_tax(self, taxes, product=None, partner=None):
        if "price_include_taxes" in self._context:
            taxes = taxes.get_equivalent_tax(
                price_include=self._context["price_include_taxes"]
            )
        return super().map_tax(taxes, product=product, partner=partner)
