# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_procurement_create(self):
        new_procs = self.env['procurement.order']
        for line in self.filtered(
                lambda sol: not sol.order_id.delivery_block_id
                and not sol.order_id.manual_delivery):
            new_procs += super(
                SaleOrderLine, line.with_context(
                    group_by_line=True))._action_procurement_create()
        return new_procs
