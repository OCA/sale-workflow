# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self, values):
        # The ctx update_delivery_shipping_partner already updates the
        # address on the related deliveries in sale_stock module
        if "partner_shipping_id" not in values or self.env.context.get(
            "update_delivery_shipping_partner"
        ):
            return super().write(values)
        new_partner = self.env["res.partner"].browse(values.get("partner_shipping_id"))
        # Pass context to prevent creating activity to update the address
        res = super(
            SaleOrder, self.with_context(skip_partner_address_activity=True)
        ).write(values)
        pickings = self.mapped("picking_ids").filtered(
            lambda x: x.state not in ("done", "cancel")
        )
        if pickings:
            pickings.partner_id = new_partner
        return res

    @api.onchange("partner_shipping_id")
    def _onchange_partner_shipping_id(self):
        # Replace the standard "do not forget to update" warning with an
        # informational message that the update will happen automatically.
        res = super()._onchange_partner_shipping_id() or {}
        if res.get("warning"):
            res["warning"] = {
                "title": _("Warning"),
                "message": _(
                    "The delivery address of the deliveries not yet processed "
                    "will be automatically updated."
                ),
            }
        return res
