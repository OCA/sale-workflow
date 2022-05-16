# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models

HELP = _(
    "Only price items with 'Based on' field set to " "'Public Price' are supported.\n"
)


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    price_include_taxes = fields.Boolean(
        string="Price include taxes",
        default=True,
        help="If checked, prices of the list are taken account tax include.\n"
        "We can only update this setting if there is no price item.",
    )

    def name_get(self):
        res = super(ProductPricelist, self).name_get()
        pricelist_ids = [x[0] for x in res]
        pricelists = self.env["product.pricelist"].browse(pricelist_ids)
        suffix = {
            x.id: _(" (tax include)") for x in pricelists if x.price_include_taxes
        }
        names = []
        for elm in res:
            names.append((elm[0], "{}{}".format(elm[1], suffix.get(elm[0], ""))))
        return names
