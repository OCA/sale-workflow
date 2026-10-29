# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def activity_schedule(
        self, act_type_xmlid="", date_deadline=None, summary="", note="", **act_values
    ):
        pickings = self
        if (
            self._context.get("skip_partner_address_activity")
            and act_type_xmlid == "mail.mail_activity_data_warning"
        ):
            # Do not create activity to update address in pickings where it
            # is already done automatically
            pickings = self.filtered(
                lambda p: not p.picking_type_id.sale_auto_update_delivery_address
            )
        return super(StockPicking, pickings).activity_schedule(
            act_type_xmlid=act_type_xmlid,
            date_deadline=date_deadline,
            summary=summary,
            note=note,
            **act_values,
        )
