# © 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    price_include_taxes = fields.Boolean(
        string="Price include taxes",
        default=False,
        help="If checked, prices of the list are taken account tax include.\n"
        "We can only update this setting if there is no price item.",
    )

    @api.depends("price_include_taxes")
    def _compute_display_name(self):  # pylint: disable=missing-return
        super()._compute_display_name()
        for pricelist in self:
            if pricelist.price_include_taxes:
                pricelist.display_name = "{}{}".format(
                    pricelist.display_name, self.env._(" (tax include)")
                )
