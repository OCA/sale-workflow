# -*- coding: utf-8 -*-
from openerp import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False,
                          context=None):
        """
        add default layout if defined on the product
        """
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, context=context)
        if product:
            pro = self.pool['product.product'].browse(
                cr, uid, product, context=context)
            res['value']['sale_layout_cat_id'] = pro.section_id and \
                    pro.section_id.id or False
        return res
