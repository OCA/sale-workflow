# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from collections import defaultdict

from odoo import _, api, models
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
        fixed_price = super(AccountTax, self)._fix_tax_included_price(
            price, prod_taxes, line_taxes
        )
        pricelist_id = self.env.context.get("pricelist")
        skip_fixing_price = False
        # Check if pricelist contains adhoc price
        if pricelist_id:
            self._check_product_sale_tax_include(prod_taxes)
            pricelist = self.env["product.pricelist"].browse(pricelist_id)
            if not pricelist.price_include_taxes:
                self._check_sale_line_tax_exclude(line_taxes, pricelist)
                # we skip odoo logic as the pricelist is tax excluded
                # with tax excluded on line so we do not have anything to remove
                skip_fixing_price = True
            elif all(line_taxes.mapped("price_include")):
                # we skip odoo logic as the pricelist is tax included
                # and the taxe line are tax included
                skip_fixing_price = True
        if skip_fixing_price:
            return price
        return fixed_price

    def _check_product_sale_tax_include(self, prod_taxes):
        prod_taxes_exclude = prod_taxes.filtered(
            lambda t: t.type_tax_use == "sale" and not t.price_include
        )
        if prod_taxes_exclude:
            raise UserError(
                _(
                    "Tax product '%s' is price exclude. "
                    "You must switch to include ones." % prod_taxes_exclude[0].name
                )
            )

    def _check_sale_line_tax_exclude(self, line_taxes, pricelist):
        line_taxes_include = line_taxes.filtered(lambda t: t.price_include)
        if line_taxes_include:
            raise UserError(
                _(
                    "Tax with include price with pricelist b2b '%s' "
                    "is not supported" % pricelist.name
                )
            )

    def _map_exclude_tax(self):
        """return a dict
        mtax[company_id or 0][tax amount]['include'|'exclude'] = tax_id
        """
        mtax = defaultdict(dict)
        prev_cpny = False
        for tax in self.search(
            [("type_tax_use", "=", "sale")], order="company_id ASC, price_include DESC"
        ):
            cpny = tax.company_id
            if cpny != prev_cpny:
                tamount = defaultdict(dict)
            if tax.price_include:
                tamount[tax.amount].update({"include": tax.id})
            else:
                tamount[tax.amount].update({"exclude": tax.id})
            if tax.amount in mtax[tax.company_id.id or 0]:
                mtax[tax.company_id.id or 0][tax.amount].update(tamount[tax.amount])
            else:
                mtax[tax.company_id.id or 0][tax.amount] = tamount[tax.amount]
            prev_cpny = cpny
        return mtax

    def _get_substitute_taxes(self, record, taxes, map_tax):
        # TODO shortify this code
        if record._name == "sale.order.line":
            cpny = record.order_id.company_id.id or self.company_id.id or 0
        elif record._name == "account.move.line":
            cpny = record.move_id.company_id.id or self.company_id.id or 0
        else:
            raise UserError(_("No other model supported than sale and invoice"))
        # TODO end
        mytaxes = []
        for tax in taxes:
            if map_tax[cpny].get(tax.amount):
                if map_tax[cpny][tax.amount].get("exclude"):
                    mytaxes.append(map_tax[cpny][tax.amount]["exclude"])
                else:
                    mytaxes.append(tax.id)
            else:
                mytaxes.append(tax.id)
        return self.env["account.tax"].browse(mytaxes)
