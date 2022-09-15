# Copyright 2022 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    block_delivery = fields.Boolean(copy=False)

    def action_release_delivery(self):
        return {
            "name": _("Release Delivery"),
            "type": "ir.actions.act_window",
            "res_model": "sale.release.delivery.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"active_id": self.id},
        }
