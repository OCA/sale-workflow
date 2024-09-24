# Copyright (C) 2015-Today GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderMassActionWizard(models.TransientModel):

    _name = "sale.order.mass.action.wizard"
    _description = "Sale Order Mass Action"

    confirm = fields.Boolean(
        help="Check this box if you want to confirm all the selected quotations."
    )

    def _get_sale_order_confirm_domain(self):
        return [
            ("id", "in", self.env.context.get("active_ids")),
            ("state", "in", ("draft", "sent")),
        ]

    @api.model
    def _notify_success(self, sale_orders):
        order_names = "\n".join(sale_orders.mapped("name"))
        message = "The following orders has been updated : %s" % order_names
        self.env.user.notify_success(message=message)

    def apply_button(self):
        sale_order_obj = self.env["sale.order"]
        if self.env.context.get("active_model") != "sale.order":
            return
        for wizard in self.filtered("confirm"):
            sale_orders = sale_order_obj.search(wizard._get_sale_order_confirm_domain())
            sale_orders.action_confirm()
            self._notify_success(sale_orders)
        return True
