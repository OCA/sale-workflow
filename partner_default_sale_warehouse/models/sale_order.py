# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L. <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_shipping_id')
    def _onchange_partner_shipping_id(self):
        """
        Override to add Operating Units to Picking.
        """
        if self.partner_shipping_id.sale_warehouse_id:
            self.warehouse_id = self.partner_shipping_id.sale_warehouse_id.id
