# -*- coding: utf-8 -*-
# © 2015-2015 Yannick Vaucher, Leonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class Procurement(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _get_stock_move_values(self):
        """Propagate owner from sale order line to stock move.

        This is run when a quotation is validated into a sale order.

        """
        res = super(Procurement, self)._get_stock_move_values()
        sale_line = self.sale_line_id
        if sale_line:
            res['restrict_partner_id'] = sale_line.stock_owner_id.id
        return res
