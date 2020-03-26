# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import timedelta

from odoo import _, exceptions, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_cutoff_time(self):
        self.ensure_one()
        partner = self.partner_shipping_id
        if partner.order_delivery_cutoff_preference == "warehouse_cutoff":
            return self.warehouse_id.get_cutoff_time()
        elif partner.order_delivery_cutoff_preference == "partner_cutoff":
            return self.partner_shipping_id.get_cutoff_time()
        else:
            raise exceptions.UserError(_("Invalid cutoff settings"))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        """Postpone delivery according to cutoff time"""
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.order_id.commitment_date:
            return res
        cutoff = self.order_id.get_cutoff_time()
        # Postpone delivery for order confirmed before cutoff to cutoff time
        new_date_planned = res.get("date_planned").replace(
            hour=int(cutoff.get("hour")), minute=int(cutoff.get("minute"))
        )
        # Postpone delivery for order confirmed after cutoff to day after
        if self.order_id.date_order > fields.Datetime.now().replace(
            hour=int(cutoff.get("hour")), minute=int(cutoff.get("minute"))
        ):
            new_date_planned += timedelta(days=1)
        res["date_planned"] = new_date_planned
        return res
