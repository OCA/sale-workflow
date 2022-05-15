# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _fix_tax_included_price(self, price, prod_taxes, line_taxes):
        """Override Odoo method to:
        - use raw price from pricelist (if price exclude)
          instead of recomputed price
        - some checks/raises on unmanaged cases
        """
        pricelist_id = self.env.context.get("pricelist")
        if pricelist_id:
            prod_taxes._ensure_price_include()
            pricelist = self.env["product.pricelist"].browse(pricelist_id)
            if not pricelist.price_include_taxes:
                line_taxes._ensure_price_exclude(pricelist)
                # we skip odoo logic as the pricelist is tax excluded
                # with tax excluded on line so we do not have anything to remove
                return price
            elif all(line_taxes.mapped("price_include")):
                # we skip odoo logic as the pricelist is tax included
                # and the taxe line are tax included
                return price
        return super()._fix_tax_included_price(price, prod_taxes, line_taxes)

    def _ensure_price_include(self):
        taxes_exclude = self.filtered(lambda s: not s.price_include)
        if taxes_exclude:
            raise UserError(
                _(
                    "Tax product '%s' is price exclude. "
                    "You must switch to include ones." % taxes_exclude[0].name
                )
            )

    def _ensure_price_exclude(self, pricelist):
        if any(self.mapped("price_include")):
            raise UserError(
                _(
                    "Tax with include price with pricelist b2b '%s' "
                    "is not supported" % pricelist.name
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
