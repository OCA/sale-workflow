# Copyright 2022 Camptocamp SA (<https://www.camptocamp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = ["sale.order"]

    def _compute_so_variant_ids(self):
        for order in self:
            variant_orders = self.search(
                [
                    ("unrevisioned_name", "=", order.unrevisioned_name),
                    ("id", "!=", order.id),
                ]
            )
            order.so_variant_count = len(variant_orders)

    def action_view_sale_order_variants(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale.act_res_partner_2_sale_order"
        )
        action["domain"] = [
            ("unrevisioned_name", "=", self.unrevisioned_name),
            ("id", "!=", self.id),
        ]
        return action

    so_variant_ids = fields.One2many(
        "sale.order", compute="_compute_so_variant_ids", string="Variants"
    )
    so_variant_count = fields.Integer(
        compute="_compute_so_variant_ids", string="Variant Count"
    )

    def _get_next_rev_number(self):
        self.ensure_one()
        all_rev = self.search([("unrevisioned_name", "=", self.unrevisioned_name)])
        return max(all_rev.mapped("revision_number")) + 1

    def _get_new_rev_data(self, new_rev_number):
        new_rev_number = self._get_next_rev_number()
        result = super()._get_new_rev_data(new_rev_number)
        result.update(
            {
                "current_revision_id": False,
            }
        )
        return result

    def _prepare_revision_data(self, new_revision):
        vals = super()._prepare_revision_data(new_revision)
        vals.pop("active")
        vals.pop("state")
        return vals

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            orders_to_cancel = (
                self.env["sale.order"]
                .with_context(active_test=False)
                .search(
                    [
                        ("unrevisioned_name", "=", order.unrevisioned_name),
                        ("id", "!=", order.id),
                    ]
                )
            )
            orders_to_cancel.action_cancel()
        return res
