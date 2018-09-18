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
        prod_taxes_exclude = [x for x in prod_taxes if not x.price_include]
        if prod_taxes_exclude:
            raise UserError(
                _("Tax product '%s' is price exclude. Switch to include ones"
                    % prod_taxes_exclude[0].get('name')))
        original = super(AccountTax, self)._fix_tax_included_price(
            price, prod_taxes, line_taxes)
        pricelist = self.env.context.get('pricelist')
        computed_price = False
        # Check if pricelist contains adhoc price
        if pricelist:
            if not self.env['product.pricelist'].browse(
                    pricelist).price_include_taxes:
                line_taxes_include = [x for x in line_taxes if x.price_include]
                if line_taxes_include:
                    raise UserError(
                        _("Tax with include price with pricelist b2b '%s' "
                          "is not supported" % pricelist.name))
                computed_price = True
        else:
            # If another module call the same method we must overide it
            # to add pricelist context in its call: let's warn us of that
            _logger.warning("Context should contains 'pricelist' key in "
                            "'_fix_tax_included_price' method")
        if computed_price:
            return price
        return original
