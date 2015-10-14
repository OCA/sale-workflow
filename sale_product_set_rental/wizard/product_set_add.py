# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class ProductSetAd(models.TransientModel):
    _inherit = 'product.set.add'
    _descritpion = "Add capability to add rental service product sets using default dates from sale order"

# add functionality only for products that have field 'must_have_dates' set
    @api.multi
    def prepare_sale_order_line_data(self, sale_order_id, set, set_line,
                                     max_sequence=0):
        if set_line.product_id.must_have_dates:
            so = self.env['sale.order'].browse(sale_order_id)
            nod = 1
            start_dt = so.default_start_date
            end_dt = so.default_end_date
            if not start_dt:
                start_dt = fields.Date.today() 
            if not end_dt:
                end_dt = fields.Date.today() 
            if start_dt > end_dt:
                end_dt = start_dt
            nod = (
                fields.Date.from_string(end_dt) -
                fields.Date.from_string(start_dt)).days + 1
            qty = self.quantity
            return {
                    'order_id': sale_order_id,
                    'product_id': set_line.product_id.id,
                    'product_uom_qty': set_line.quantity * self.quantity,
                    'sequence': max_sequence + set_line.sequence,
                    'start_date': start_dt,
                    'end_date': end_dt,
                    'number_of_days': nod,
                    'rental_qty': qty,
                    'product_uom_qty': nod * qty,
                    'rental': True,
                    'rental_type': 'new_rental',
            }
        else:
            return super(ProductSetAd, self).prepare_sale_order_line_data(
                        sale_order_id, set, set_line, max_sequence)
