# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _notify_get_groups(self, msg_vals=None):
        """
        Reverse base behaviour from Odoo core. We don't always want
        portal_customer to access the ERP
        partner_id evaluates to portal_customer !
        """
        groups = super(SaleOrder, self)._notify_get_groups(msg_vals=msg_vals)
        if self.state not in ("draft", "cancel"):
            for group_name, _group_method, group_data in groups:
                if group_name == "portal_customer":
                    group_data["has_button_access"] = False
        return groups
