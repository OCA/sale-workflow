# Copyright 2013 Julius Network Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_search_vals_for_quantity(self, line):
        return [
            ('order_id', '=', line.order_id.id),
            ('state', '!=', 'cancel'),
            ('product_id.categ_id', '=', line.product_id.categ_id.id),
        ]

    def _get_quantity_to_compute(self, line):
        quantity = line.product_uom_qty
        if line.product_id:
            order_line_obj = self.env['sale.order.line']
            search_domain = self._get_search_vals_for_quantity(line)
            line_ids = order_line_obj.search(search_domain)
            quantity = sum([x.product_uom_qty for x in line_ids])
        return quantity

    def _get_price_of_line(self, product_id,
                           qty, partner_id, pricelist_id):
        return self.env['product.pricelist']._price_rule_get_multi(
            pricelist=pricelist_id,
            products_by_qty_by_partner=[(product_id, qty, partner_id)])

    def _check_if_edit(self, res, product_id):
        if res.get(product_id):
            price, item_id = res.get(product_id, False)
            if item_id:
                item = self.env['product.pricelist.item'].browse(item_id)
                if item.categ_id:
                    return True
        return False

    def _get_child_pricelist(self, res):
        if res.get('item_id'):
            item_id = res.get('item_id', False)
            if item_id:
                item = self.env['product.pricelist.item'].browse(item_id)
                if item.base_pricelist_id:
                    return item.base_pricelist_id
        return False

    def compute_global_discount(self):
        for sale in self:
            if sale.state in ['draft', 'sent']:
                sale.order_line.compute_global_discount()
        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def compute_global_discount(self):
        for line in self:
            sale = line.order_id.with_context(date=line.order_id.date_order)
            partner_id = sale.partner_id.id
            if line.product_id:
                pricelist_id = sale.pricelist_id
                product_id = line.product_id
                qty = sale._get_quantity_to_compute(line)
                if qty:
                    res = sale._get_price_of_line(
                        product_id, qty, partner_id, pricelist_id)
                    while True:
                        new_pricelist_id = sale._get_child_pricelist(res)
                        if not new_pricelist_id:
                            break
                        res = sale._get_price_of_line(product_id,
                                                      qty, partner_id,
                                                      new_pricelist_id)
                        pricelist_id = new_pricelist_id
                    price_unit = False
                    if sale._check_if_edit(res, line.product_id.id):
                        price_unit = res.get(
                            line.product_id.id, {})[0]
                    else:
                        price_unit = pricelist_id.with_context(
                            date=line.order_id.date_order).price_get(
                            product_id.id, line.product_uom_qty,
                            partner=sale.partner_id.id)[pricelist_id.id]
                    if price_unit is not False:
                        line.write({'price_unit': price_unit})
        return True
