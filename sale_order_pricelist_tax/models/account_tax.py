# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _ensure_price_include(self):
        taxes_exclude = self.filtered(lambda s: not s.price_include)
        if taxes_exclude:
            raise UserError(
                _(
                    "Tax product '%s' is price exclude. "
                    "You must switch to include ones." % taxes_exclude[0].name
                )
            )

    def get_equivalent_tax_exc(self):
        taxes = self.browse(False)
        for record in self:
            taxes |= self.browse(self._get_equivalent_tax_exc_id(record.id))
        return taxes

    @tools.ormcache("tax_inc_id")
    def _get_equivalent_tax_exc_id(self, tax_inc_id):
        tax_inc = self.browse(tax_inc_id)
        tax_inc._ensure_price_include()
        tax = self.search(
            [
                ("price_include", "=", False),
                ("company_id", "=", tax_inc.company_id.id),
                ("type_tax_use", "=", tax_inc.type_tax_use),
                ("amount", "=", tax_inc.amount),
            ]
        )
        if not tax:
            raise UserError(
                _("Equivalent price exclude tax for '%s' is missing" % tax_inc.name)
            )
        else:
            return tax.id

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
