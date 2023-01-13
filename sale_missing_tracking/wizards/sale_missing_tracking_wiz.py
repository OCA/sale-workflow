# Copyright 2021 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleMissingTrackingWiz(models.TransientModel):
    _name = "sale.missing.tracking.wiz"
    _description = "Sale missing tracking wizard"

    missing_tracking_ids = fields.Many2many(
        comodel_name="sale.missing.tracking",
    )
    reason_id = fields.Many2one(comodel_name="sale.missing.tracking.reason")
    reason_note = fields.Text(
        compute="_compute_reason_note", store=True, readonly=False
    )
    has_pending_lines = fields.Boolean(compute="_compute_has_pending_lines")

    @api.depends("reason_id")
    def _compute_reason_note(self):
        for rec in self:
            rec.reason_note = rec.reason_id.note

    @api.depends("missing_tracking_ids.reason_id")
    def _compute_has_pending_lines(self):
        self.has_pending_lines = bool(
            self.missing_tracking_ids.filtered(lambda ln: not ln.reason_id)
        )

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, _("Sale missing tracking")))
        return result

    def action_mass_update(self):
        self.missing_tracking_ids.update(
            {"reason_id": self.reason_id.id, "reason_note": self.reason_note}
        )

    def _check_conditions_to_confirm(self):
        """ """
        empty_reason_lines = self.missing_tracking_ids.filtered(
            lambda tr: not tr.reason_id
        )
        if empty_reason_lines:

            groups = self.env["sale.missing.tracking"].read_group(
                domain=[
                    ("product_id", "in", empty_reason_lines.mapped("product_id").ids),
                    ("partner_id", "in", empty_reason_lines.mapped("partner_id").ids),
                    ("reason_id", "=", False),
                    ("order_id.state", "in", ["sale", "done"]),
                ],
                fields=["partner_id", "product_id"],
                groupby=["partner_id", "product_id"],
                lazy=False,
            )
            message = ""
            max_delay_times = self.env.company.sale_missing_max_delay_times
            for group in groups:
                if group["__count"] >= max_delay_times:
                    message += "%s\n" % group["product_id"][1]
            if message:
                message = (
                    _(
                        "You cannot postpone this advice any more times."
                        "Why doesn't the customer buy these products?\n"
                    )
                    + message
                )
            return message

    def missing_tracking_action_confirm(self):
        """Check conditions to allow to confirm a sale order"""
        message_conditions = self._check_conditions_to_confirm()
        if message_conditions:
            raise ValidationError(message_conditions)
        sale_orders = self.with_context(
            bypass_missing_cart_tracking=True
        ).missing_tracking_ids.mapped("order_id")
        sale_orders.action_confirm()
        return self.action_open_sale_order(sale_orders)

    def action_open_sale_order(self, sale_orders=None):
        if sale_orders is None:
            sale_orders = self.with_context(
                bypass_missing_cart_tracking=True
            ).missing_tracking_ids.mapped("order_id")
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        if len(sale_orders) == 1:
            view = self.env.ref("sale.view_order_form", False)
            action["views"] = [(view and view.id or False, "form")]
            action["res_id"] = sale_orders.id
        else:
            action["domain"] = [("id", "in", sale_orders.ids)]
        return action
