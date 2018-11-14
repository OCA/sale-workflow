# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_launch_procurement_rule(self):
        return super(SaleOrderLine, self.filtered(
            lambda line: not line.order_id.delivery_block_id)). \
            _action_launch_procurement_rule()
