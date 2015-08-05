# -*- encoding: utf-8 -*-
from openerp import models


class SaleOrderBundle(models.TransientModel):
    _inherit = 'sale.order.bundle'

    def prepare_sale_order_line_data(self, sale_order_id, bundle, bundle_line,
                                     *args, **kwargs):
        sol_data = super(SaleOrderBundle, self).prepare_sale_order_line_data(
            sale_order_id, bundle, bundle_line, *args, **kwargs)
        sol_data.update({'sale_layout_cat_id': bundle.section_id.id})
        return sol_data
