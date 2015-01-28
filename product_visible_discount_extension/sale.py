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
        for record in self:

            if record.list_price and record.temp_value is False:

                if record.price_unit < record.list_price:
                    new_price = (record.list_price - record.price_unit) * 100
                    record.visible_discount = new_price / record.list_price
                else:
                    record.visible_discount = 0

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
        for record in self:

            if record.product_id.list_price and record.temp_value is False:

                record.price_unit = ((100 - record.visible_discount) / 100
                                     * record.list_price)
                record.temp_value = record.visible_discount

                if record.visible_discount < 0:
                    record.visible_discount = 0

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

        if 'price_unit' in res['value']:
            if res['value']['discount'] == 0:
                product_obj = self.pool.get('product.product')
                product = product_obj.browse(cr, uid, product, context)
                price_list = product.list_price
                new_discount = (1 - res['value']['price_unit'] / price_list)
                res['value']['visible_discount'] = new_discount * 100
            else:
                new_price = ((100 - res['value']['discount']) *
                             res['value']['price_unit'])
                res['value']['price_unit'] = new_price
                res['value']['visible_discount'] = res['value']['discount']
                res['value']['discount'] = 0

        return res


    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        base = super(SaleOrderLine, self)
        prepare_func = base._prepare_order_line_invoice_line
        vals = prepare_func(cr, uid, line, account_id, context)
        vals['visible_discount'] = line.visible_discount
        return vals
