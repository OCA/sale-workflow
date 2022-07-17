# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    equivalent_tax_inc_id = fields.Many2one(
        "account.tax",
        domain="""[
            ('price_include', '=', not price_include),
            ('company_id', '=', company_id),
            ('type_tax_use', '=', type_tax_use),
            ('amount', '=', amount),
            ]""",
        string="Equivalent Tax Inc",
    )
    # Note event it's a One2many in business point of view it's a One2one
    # This is why it end with "_id" and it's readonly
    equivalent_tax_exc_id = fields.One2many(
        "account.tax",
        "equivalent_tax_inc_id",
        string="Equivalent Tax Exc",
        readonly=True,
        copy=False,
    )

    @api.model
    def _fill_equivalent_tax_inc_id(self):
        for tax in self.search([("price_include", "=", False)]):
            tax.equivalent_tax_inc_id = self.search(
                [
                    ("price_include", "=", True),
                    ("company_id", "=", tax.company_id.id),
                    ("type_tax_use", "=", tax.type_tax_use),
                    ("amount", "=", tax.amount),
                ],
                limit=1,
            )

    def get_equivalent_tax(self, price_include):
        taxes = self.browse(False)
        for record in self:
            if record.price_include == price_include:
                taxes |= record
            else:
                if price_include:
                    if record.equivalent_tax_inc_id:
                        taxes |= record.equivalent_tax_inc_id
                    else:
                        raise UserError(
                            _(
                                "Equivalent tax include for '%s' is missing"
                                % record.name
                            )
                        )
                else:
                    if record.equivalent_tax_exc_id:
                        taxes |= record.equivalent_tax_exc_id
                    else:
                        raise UserError(
                            _(
                                "Equivalent tax exclude for '%s' is missing"
                                % record.name
                            )
                        )
        return taxes
