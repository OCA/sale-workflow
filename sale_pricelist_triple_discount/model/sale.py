#  Copyright (c) 2019 Simone Rubino - Agile Business Group
#  Copyright (c) 2021 Andrea Cometa - Apulia Software s.r.l.
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    """
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()

        if self.product_id:
            current_pricelist = self.order_id.pricelist_id
            list_price = current_pricelist.price_rule_get(
                self.product_id.id, self.product_uom_qty or 1.0,
                self.order_id.partner_id.id)
            rule_id = (list_price.get(current_pricelist.id) and
                    list_price[current_pricelist.id][1] or False)
            rule = self.env['product.pricelist.item'].browse(rule_id)
            read_rule = rule.read(['discount2', 'discount3'])[0]
            self.discount2 = read_rule['discount2'] or 0.00
            self.discount3 = read_rule['discount3'] or 0.00
        return res
    """


    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        res = super(SaleOrderLine, self)._onchange_discount()

        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('sale.group_discount_per_so_line')):
            return

        current_pricelist = self.order_id.pricelist_id
        list_price = current_pricelist.price_rule_get(
            self.product_id.id, self.product_uom_qty or 1.0,
            self.order_id.partner_id.id)
        rule_id = (list_price.get(current_pricelist.id) and
                list_price[current_pricelist.id][1] or False)
        rule = self.env['product.pricelist.item'].browse(rule_id)
        read_rule = rule.read(['discount2', 'discount3'])[0]
        self.discount2 = read_rule['discount2'] or 0.00
        self.discount3 = read_rule['discount3'] or 0.00
