# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    def get_equivalent_tax(self, price_include):
        taxes = self.browse(False)
        for record in self:
            if record.price_include == price_include:
                taxes |= record
            else:
                taxes |= self.browse(self._get_equivalent_tax(record.id, price_include))
        return taxes

    @tools.ormcache("tax_id", "price_include")
    def _get_equivalent_tax(self, tax_id, price_include):
        tax = self.browse(tax_id)
        mapped_tax = self.search(
            [
                ("price_include", "=", price_include),
                ("company_id", "=", tax.company_id.id),
                ("type_tax_use", "=", tax.type_tax_use),
                ("amount", "=", tax.amount),
            ]
        )
        if not mapped_tax:
            if price_include:
                raise UserError(
                    _("Equivalent tax include for '%s' is missing" % tax.name)
                )
            else:
                raise UserError(
                    _("Equivalent tax exclude for '%s' is missing" % tax.name)
                )
        else:
            return mapped_tax.id

    def write(self, vals):
        self.clear_caches()
        return super().write(vals)

    @api.model_create_multi
    def create(self, list_vals):
        self.clear_caches()
        return super().create(list_vals)

    def unlink(self):
        self.clear_caches()
        return super().unlink()
