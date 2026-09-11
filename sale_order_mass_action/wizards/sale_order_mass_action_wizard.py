# Copyright (C) 2015-Today GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderMassActionWizard(models.TransientModel):
    _name = "sale.order.mass.action.wizard"
    _description = "Sale Order Mass Action"

    action = fields.Selection(
        [
            ("confirm", "Confirm"),
            ("quotation_sent", "Send Quotation"),
            ("lock", "Lock"),
            ("unlock", "Unlock"),
            ("cancel", "Cancel"),
            ("draft", "Set to Draft"),
        ]
    )

    def _get_sale_order_state_domain(self):
        self.ensure_one()
        if self.action == "confirm":
            return [("state", "in", ("draft", "sent"))]
        elif self.action == "quotation_sent":
            return [("state", "=", "draft")]
        elif self.action == "cancel":
            return [("state", "=", "draft")]
        elif self.action == "draft":
            return [("state", "in", ("cancel", "sent"))]
        elif self.action in ("lock", "unlock"):
            return []

    def _get_sale_order_domain(self):
        self.ensure_one()
        domain = [("id", "in", self.env.context.get("active_ids"))]
        domain = fields.Domain.AND([domain, self._get_sale_order_state_domain()])
        return domain

    def _launch_action(self, sale_orders):
        self.ensure_one()
        action = "action_" + self.action
        if hasattr(sale_orders, action):
            getattr(sale_orders, action)()
            return True
        return False

    @api.model
    def _notify_success(self, sale_orders):
        order_names = "\n".join(sale_orders.mapped("name"))
        message = self.env._(
            "The following orders has been updated : %(order_names)s",
            order_names=order_names,
        )
        self.env.user.notify_success(message=message)

    def apply_button(self):
        sale_order_obj = self.env["sale.order"]
        if self.env.context.get("active_model") != "sale.order":
            return
        for wizard in self:
            sale_orders = sale_order_obj.search(wizard._get_sale_order_domain())
            if wizard._launch_action(sale_orders=sale_orders):
                self._notify_success(sale_orders)
        return True
