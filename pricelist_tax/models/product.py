# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

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

    @api.multi
    @api.constrains("price_include_taxes")
    def _constrains_pricelist_price_include(self):
        for rec in self:
            items = self.env["product.pricelist.item"].search(
                [("pricelist_id", "=", rec.id), ("base", "!=", "list_price")]
            )
            if items:
                raise UserError(
                    HELP
                    + _(
                        "\nSome of them are of another type like here '%s'\n"
                        "of type '%s' " % (items[0], items[0].base)
                    )
                )

    @api.multi
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


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    @api.multi
    @api.constrains("base")
    def _constrains_price_item_price_include(self):
        for rec in self:
            price_incl_tax = rec.pricelist_id.price_include_taxes
            if rec.base in ("pricelist", "standard") and price_incl_tax:
                raise UserError(
                    HELP + _("You encoded 'Based on' field to %s" % rec.base)
                )
