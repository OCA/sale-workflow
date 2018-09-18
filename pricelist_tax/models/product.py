# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    price_include_taxes = fields.Boolean(
        string=u"Prix en TTC", default=True,
        help=u"Si coché les prix de cette liste de prix doivent être en TTC\n"
             u"sinon en HT.\n"
             u"On ne peut modifier ce champ que s'il n'y a pas "
             u"de règle de prix associée")

    @api.multi
    @api.constrains('price_include_taxes')
    def _constrains_pricelist_price_include(self):
        for rec in self:
            items = self.env['product.pricelist.item'].search(
                [('pricelist_id', '=', rec.id),
                 ('base', '!=', 'list_price')])
            if items:
                raise UserError(_(
                    u"Il y a des règles de prix comme %s qui ont le champ \n"
                    u"base incompatible avec la taxe défini sur la "
                    u"liste de prix" % items[0]))

    @api.multi
    def name_get(self):
        res = super(ProductPricelist, self).name_get()
        pricelist_ids = [x[0] for x in res]
        pricelists = self.env['product.pricelist'].browse(pricelist_ids)
        suffix = {x.id: ' (TTC)' for x in pricelists if x.price_include_taxes}
        names = []
        for elm in res:
            names.append((elm[0], '%s%s' % (elm[1], suffix.get(elm[0], ''))))
        return names


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    @api.multi
    @api.constrains('base')
    def _constrains_price_item_price_include(self):
        for rec in self:
            price_incl_tax = rec.pricelist_id.price_include_taxes
            if rec.base in ('pricelist', 'standard') and price_incl_tax:
                    raise UserError(_(
                        u"Vous avez utilisé un prix basé sur une autre "
                        u"liste de prix qui est incompatible avec "
                        u"celle-ci (case à cocher TTC)."))
