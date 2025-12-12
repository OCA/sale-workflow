# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_cancel(self):
        if (
            not self.env.context.get("disable_cancel_warning")
            and self.env.company.enable_sale_cancel_restrict
        ):
            for rec in self:
                if any(delivery.state == "done" for delivery in rec.picking_ids):
                    raise ValidationError(
                        self.env._(
                            "You cannot cancel the SO: %(so_name)s as it "
                            "has some transfers already done.",
                            so_name=rec.name,
                        )
                    )
                if any(invoice.state != "cancel" for invoice in rec.invoice_ids):
                    raise ValidationError(
                        self.env._(
                            "You cannot cancel the SO: %(so_name)s as "
                            "it has some invoices in draft "
                            "or posted state. Please cancel them "
                            "to be able to cancel the SO.",
                            so_name=rec.name,
                        )
                    )
        return super()._action_cancel()
