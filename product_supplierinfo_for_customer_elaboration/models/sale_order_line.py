# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        customerinfo = self.product_id.customer_ids.filtered(
            lambda pc: pc.elaboration_id and pc.name == self.order_id.partner_id
        )[:1]
        if not customerinfo:
            customerinfo = self.product_id.customer_ids.filtered(
                lambda pc: pc.elaboration_id
                and pc.name == self.order_id.partner_id.commercial_partner_id
            )[:1]
        if customerinfo:
            self.elaboration_id = customerinfo.elaboration_id
        if customerinfo.elaboration_note:
            self.elaboration_note = customerinfo.elaboration_note
        return res
