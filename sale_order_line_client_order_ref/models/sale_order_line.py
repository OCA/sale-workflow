# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    client_order_ref = fields.Char(
        "Customer Order Ref",
        compute="_compute_client_order_ref",
        store=True,
        readonly=False,
    )

    def _get_so_line_client_ref_policy(self):
        self.ensure_one()
        return (
            self.order_partner_id.so_line_client_ref_policy
            or self.company_id.so_line_client_ref_policy
        )

    @api.depends("order_id.client_order_ref")
    def _compute_client_order_ref(self):
        for rec in self:
            policy = rec._get_so_line_client_ref_policy()
            if policy == "sync":
                rec.client_order_ref = rec.order_id.client_order_ref

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res["client_order_ref"] = self.client_order_ref
        if (
            self.client_order_ref
            and self.company_id.client_order_ref_in_invoice_line_desc
        ):
            self_lang = self.with_context(lang=self.order_id.partner_invoice_id.lang)
            label = self_lang.env._("Customer Order Ref:")
            res["name"] = f"[{label} {self.client_order_ref}]\n{res['name']}"
        return res
