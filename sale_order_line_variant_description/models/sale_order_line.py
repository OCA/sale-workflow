# -*- coding: utf-8 -*-
# © 2015 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0, uom=False, qty_uos=0,
            uos=False, name='', partner_id=False, lang=False,
            update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False
    ):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist=pricelist, product=product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name,
            partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        if product:
            product_obj = self.env['product.product']
            lang = self.env['res.partner'].browse(partner_id).lang
            product = product_obj.with_context(lang=lang).browse(product)
            if product.variant_description_sale:
                if 'value' not in res:
                    res['value'] = {}
                res['value']['name'] = product.variant_description_sale
        return res
