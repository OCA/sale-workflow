from openerp import models, fields
from openerp import api

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
    visible_discount = fields.Float('Discount (%)')

    # We have to store a value in our model to keep track of changes..
    temp_value = fields.Float('Track changes to the price_unit', store=False)


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
                    record.visible_discount = ((record.list_price - record.price_unit)
                                       * 100 / record.list_price)
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

            if record.list_price and record.temp_value is False:
                if record.discount > 0:
                    record.visible_discount = record.discount
                    record.discount = 0

                record.price_unit = ((100 - record.visible_discount) / 100
                                     * record.list_price)
                record.temp_value = record.visible_discount

    #@api.one
    #def write(self, values, context=None):
    #    import pdb; pdb.set_trace()
    #    self._columns['price_subtotal']._fnct = compute_amount_line
    #    super(SaleOrderLine, self).write(values)
