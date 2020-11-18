# Copyright 2014 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2015 Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def recalculate_prices(self):
        for line in self.mapped('order_line'):
            vals = line.play_onchanges({}, ['product_id', 'product_uom_qty'])
            line.write(vals)

    @api.multi
    def recalculate_taxes(self):
        # Force updating stored field by calling `_compute_amount`
        model = self.env['sale.order.line']
        self.env.add_todo(
            model._fields['price_tax'],
            self.mapped('order_line'),
        )
        return model.recompute()

    @api.multi
    def recalculate_names(self):
        for line in self.mapped('order_line').filtered('product_id'):
            # we make this to isolate changed values:
            line2 = self.env['sale.order.line'].new(
                {
                    'product_id': line.product_id,
                }
            )
            line2.product_id_change()
            line.name = line2.name
        return True
