from openerp import models, fields
from openerp import api

from logging import Logger

class SaleOrderLine(models.Model):

    """
    Compute the value of discount and price_unit.

    As those two fields are mutual, we have to store a value in a 
    temp variable.

    Any change to discount will trigger onchanges events in that order:
        _onchange_discount
        _onchange_price
        _onchange_discount

    Any change to price_unit will trigger onchange events in that order:
        _onchange_price
        _onchange_discount
        _onchange_price
    """

    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    #lst_price = fields.Many2one('product.pricelist', 'Price list')
    list_price = fields.Float('Price list', related="product_id.list_price", store=True, readonly=True)

    # We have to store a value in our model to keep track of changes..
    temp_value = fields.Float('Track changes to the price_unit', store=False)

    @api.onchange('price_unit')
    def _onchange_price(self):
        """
        Compute the discount when the price_unit change.

        This method changes the price_unit value to this:

            discount = (list_price - price_unit) * 100 / list_price
        """
        for record in self:

            if record.list_price:
                if record.price_unit < record.list_price:
                    record.discount = (record.list_price - record.price_unit) * 100 / record.list_price
                else:
                    record.discount = 0

                if record.temp_value >= 0 and not record.temp_value is False:
                    record.discount = record.temp_value
                    record.temp_value = -1
                elif record.temp_value == False:
                    record.temp_value = record.price_unit



    @api.onchange('discount')
    def _onchange_discount(self):
        """
        Compute the price_unit based on the discount value.

        This method is triggered whenever the discount is changed.
        When the discount is changed, the value of price_unit is 
        changed using this formula:

            price_unit = discount / 100 * list_price
        """
            
        for record in self:

            if record.list_price:

                if record.discount == 0:
                    record.price_unit = record.list_price
                else:
                    record.price_unit =  record.discount / 100 * record.list_price

                if record.temp_value >= 0 and not record.temp_value is False:
                    record.price_unit = record.temp_value
                    record.temp_value = -1
                elif record.temp_value == False:
                    record.temp_value = record.discount
