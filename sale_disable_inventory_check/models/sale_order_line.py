# Copyright Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        res = \
            super(SaleOrderLine,
                  self)._onchange_product_id_check_availability()
        if self.product_id \
                and not self.product_id.product_tmpl_id._check_stock_on_sale():
            if res.get('warning', {}).get('title') == _(
                    'Not enough inventory!'):
                res.pop('warning')
        return res
