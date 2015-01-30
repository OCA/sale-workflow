# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.exceptions import ValidationError
from openerp import (
    models,
    fields,
    api,
)


class SaleOrderLine(models.Model):

    """
    Compute the value of visible_discount and price_unit.

    As those two fields are mutual, we have to store a value in a
    temp variable.

    Any change to visible_discount will trigger onchanges events in that order:
        _onchange_visible_discount
        _onchange_price

    Any change to price_unit will trigger onchange events in that order:
        _onchange_price
        _onchange_visible_discount
    """

    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    list_price = fields.Float('Price list',
                              related="product_id.list_price",
                              store=True,
                              readonly=True)
    visible_discount = fields.Float('Customer  Discount (%)')

    # We have to store a value in our model to keep track of changes..
    temp_value = fields.Float('Track changes to the price_unit', store=False)

    @api.constrains('visible_discount')
    def _check_visible_discount(self):
        """
        Constrain the visible_discount.

        The visible_discount should not big more than 100%. If the
        value becomes more than 100%, then the price of the product
        will become negative.
        """
        if self.visible_discount > 100:
            raise ValidationError("The discount cannot be more than 100%")

    @api.onchange('price_unit')
    def _onchange_price(self):
        """
        Compute the visible_discount when the price_unit change.

        This method changes the price_unit value to this:

            visible_discount = (list_price - price_unit) * 100 / list_price
        """
        decimal_precision = self.env['decimal.precision']
        precision = decimal_precision.precision_get('Account')

        for record in self:

            if record.list_price and record.temp_value is False:

                if record.price_unit < record.list_price:
                    new_price = (record.list_price - record.price_unit)
                    discount = new_price / record.list_price * 100
                    discount = round(discount, precision)
                    record.visible_discount = discount
                else:
                    record.visible_discount = 0

                record.temp_value = record.price_unit
            else:
                record.visible_discount = record.temp_value
                record.temp_value = record.price_unit

    @api.onchange('visible_discount', 'discount')
    def _onchange_visible_discount(self):
        """
        Compute the price_unit based on the visible_discount value.

        This method is triggered whenever the visible_discount is changed.
        When the visible_discount is changed, the value of price_unit is
        changed using this formula:

            price_unit = (100 - visible_discount) / 100 * list_price
        """
        decimal_precision = self.env['decimal.precision']
        precision = decimal_precision.precision_get('Account')

        for record in self:

            if record.product_id.list_price and record.temp_value is False:

                discount = 100 - record.visible_discount
                new_price = discount * record.list_price / 100
                record.price_unit = round(new_price, precision)
                record.temp_value = record.visible_discount

                if record.visible_discount < 0:
                    record.visible_discount = 0
            else:
                record.price_unit = record.temp_value
                record.temp_value = record.visible_discount

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):
        """
        Setup the sale_order_line.

        When the sale_order_line are modified by the module
        product_visible_discount. It changes the amount for price_unit
        and discount. We convert any change in price as a discount.

        It convert discount, fixed price and mix of fixed price + discount
        to a fixed discount amount.
        """
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name,
            partner_id, lang, update_tax, date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context)

        decimal_precision = self.pool.get('decimal.precision')
        precision = decimal_precision.precision_get(cr, uid, 'Account')

        if 'price_unit' in res['value']:
            if res['value']['discount'] == 0:
                # If the pricelist has a fixed price it doesn't set
                # a discount
                product_obj = self.pool.get('product.product')
                product = product_obj.browse(cr, uid, product, context)
                price_list = product.list_price

                new_discount = res['value']['price_unit'] / price_list
                new_discount = 100 - round(new_discount, precision) * 100
            else:
                # If the pricelist doesn't have a fixed price it only
                # set a discount %
                new_price = ((100 - res['value']['discount']) *
                             res['value']['price_unit']) / 100
                new_price = round(new_price, precision)
                res['value']['price_unit'] = new_price

                new_discount = round(res['value']['discount'], precision)

            res['value']['temp_value'] = res['value']['price_unit']
            res['value']['discount'] = 0.0
            res['value']['visible_discount'] = new_discount

        return res

    def _prepare_order_line_invoice_line(self, cr, uid, line,
                                         account_id=False, context=None):
        """
        Add the visible_discount to invoice lines.

        In order to show the correct discount on the invoice form, we have to
        add its value to the invoice lines.
        """
        base = super(SaleOrderLine, self)
        prepare_func = base._prepare_order_line_invoice_line
        vals = prepare_func(cr, uid, line, account_id, context)
        vals['visible_discount'] = line.visible_discount
        return vals
