# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _fix_tax_included_price(self, price, prod_taxes, line_taxes):
        """ Override Odoo method to:
            - use raw price from pricelist (if price exclude)
              instead of recomputed price
            - some checks/raises on unmanaged cases
        """
        self._check_unsupported_case(prod_taxes=prod_taxes)
        original = super(AccountTax, self)._fix_tax_included_price(
            price, prod_taxes, line_taxes)
        pricelist_id = self.env.context.get('pricelist')
        computed_price = False
        # Check if pricelist contains adhoc price
        if pricelist_id:
            pricelist = self.env['product.pricelist'].browse(pricelist_id)
            if not pricelist.price_include_taxes:
                computed_price = True
                self._check_unsupported_case(
                    line_taxes=line_taxes, pricelist=pricelist)
        if computed_price:
            return price
        return original

    def _check_unsupported_case(
            self, prod_taxes=None, line_taxes=None, pricelist=None):
        if prod_taxes:
            prod_taxes_exclude = [x for x in prod_taxes if not x.price_include]
            if prod_taxes_exclude:
                raise UserError(
                    _("Tax product '%s' is price exclude. "
                      "Switch to include ones"
                      % prod_taxes_exclude[0].get('name')))
        if  line_taxes:
            line_taxes_include = [x for x in line_taxes if x.price_include]
            if line_taxes_include:
                raise UserError(
                    _("Tax with include price with pricelist b2b '%s' "
                        "is not supported" % pricelist.name))
