# -*- coding: utf-8 -*-
from odoo import models


class ProductSetAd(models.TransientModel):
    _inherit = 'product.set.add'

    def prepare_sale_order_line_data(self, sale_order_id, set, set_line,
                                     *args, **kwargs):
        sol_data = super(ProductSetAd, self).prepare_sale_order_line_data(
            sale_order_id, set, set_line, *args, **kwargs)

        if set.section_id.id:
            sol_data.update({'layout_category_id': set.section_id.id})
        return sol_data
