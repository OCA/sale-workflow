# -*- encoding: utf-8 -*-
from openerp import models


class ProductSetAd(models.TransientModel):
    _inherit = 'product.set.add'

    def prepare_sale_order_line_data(self, sale_order_id, set, set_line,
                                     *args, **kwargs):
        sol_data = super(ProductSetAd, self).prepare_sale_order_line_data(
            sale_order_id, set, set_line, *args, **kwargs)
        sol_data.update({'sale_layout_cat_id': set.section_id.id})
        return sol_data
