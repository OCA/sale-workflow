# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class SaleChangePrice(models.TransientModel):
    _name = 'sale.change.price'
    _description = 'Wizard to change price of sale order line'

    item_ids = fields.One2many(comodel_name='sale.change.price.item',
                               inverse_name='change_price_id',
                               string='Items')

    @api.model
    def default_get(self, field_list):
        res = super(SaleChangePrice, self).default_get(field_list)
        sale_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model')

        assert len(sale_ids) == 1, 'Bad context propagation'
        assert active_model == 'sale.order', 'Bad context propagation'

        sale_order = self.env[active_model].browse(sale_ids)

        items = []
        for order_line in sale_order.order_line:
            if not order_line.invoiced and order_line.state not in ('cancel'):
                item = {'sale_order_line_id': order_line.id,
                        'name': order_line.name,
                        'price_unit': order_line.price_unit,
                        'discount': order_line.discount
                        }
                items.append(item)

        res.update(item_ids=items)
        return res

    @api.multi
    def change_price(self):
        """ Change price and discount on sale order line """
        self.item_ids.change_price()
        return True


class SaleChangePriceItem(models.TransientModel):
    _name = 'sale.change.price.item'

    change_price_id = fields.Many2one(comodel_name='sale.change.price')
    sale_order_line_id = fields.Many2one(comodel_name='sale.order.line',
                                         string="Line", required=True)
    name = fields.Text('Description', readonly=True)
    price_unit = fields.Float(
        'Unit Price', required=True,
        digits_compute=dp.get_precision('Product Price'))
    discount = fields.Float(
        'Discount (%)', digits_compute=dp.get_precision('Discount'))

    @api.one
    def change_price(self):
        self.sale_order_line_id.write({'price_unit': self.price_unit,
                                       'discount': self.discount})
        return True
