# Copyright Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import config


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if (config['test_enable'] and
                not self.env.context.get('test_sale_disable_inventory_check')):
            return super()._onchange_product_id_check_availability()
        return {}
