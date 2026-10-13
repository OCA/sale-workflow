# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleBlanketOrderAdvancedVersionWizard(models.Model):
    _name = "sale.blanket.order.advanced.version.wizard"
    _description = "Wizard to Create Advanced Versions of Sale Blanket Orders"

    old_blanket_order_id = fields.Many2one(
        comodel_name="sale.blanket.order",
        string="Original Blanket Order",
        ondelete="cascade",
        readonly=True,
        required=True,
    )
    new_blanket_order_id = fields.Many2one(
        comodel_name="sale.blanket.order",
        string="New Version Blanket Order",
        ondelete="cascade",
        readonly=True,
    )
    price_adjustment_percent = fields.Float(
        string="Price Adjustment %",
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        blanket_order_id = self.env.context.get("default_old_blanket_order_id")
        if blanket_order_id:
            defaults["old_blanket_order_id"] = blanket_order_id
        return defaults

    def _get_version_number(self):
        count = 1
        previous = (
            self.env["sale.blanket.order.advanced.version.wizard"]
            .sudo()
            .search([("new_blanket_order_id", "=", self.old_blanket_order_id.id)])
        )
        if previous:
            count += previous._get_version_number()
        return count

    def _get_next_version_name(self):
        base = re.sub(r"\(Ver \d+\)$", "", self.old_blanket_order_id.name).strip()
        next_ver = self._get_version_number()
        return _("%(base)s (Ver %(version)s)") % {"base": base, "version": next_ver}

    def _sync_order_lines(self, old_order, new_order):
        new_order.write(
            {
                "sale_order_plan_ids": old_order.sale_order_plan_ids.ids,
                "use_sale_order_plan": old_order.use_sale_order_plan,
                "order_product_ids": old_order.order_product_ids.ids,
                "order_service_ids": old_order.order_service_ids.ids,
            }
        )
        for old_line, new_line in zip(
            old_order.line_ids,
            new_order.line_ids,
            strict=True,
        ):
            new_line.write(
                {
                    "original_uom_qty": old_line.remaining_uom_qty,
                    "contracted_qty": old_line.original_uom_qty,
                }
            )
            if self.price_adjustment_percent:
                new_line.price_unit *= 1 + (self.price_adjustment_percent / 100)
            old_line.write(
                {
                    "contracted_qty": old_line.original_uom_qty,
                    "original_uom_qty": old_line.invoiced_uom_qty,
                }
            )

    def _duplicate_order(self):
        default_data = self.old_blanket_order_id.default_get([])
        default_data.update({"name": self._get_next_version_name()})
        return self.old_blanket_order_id.copy(default_data)

    def create_version(self):
        for rec in self:
            if not rec.old_blanket_order_id.all_sale_orders_invoiced:
                raise UserError(
                    _(
                        "All sale orders must be fully invoiced before creating "
                        "a new version."
                    )
                )
            new_order = rec._duplicate_order()
            rec.new_blanket_order_id = new_order.id
            rec.old_blanket_order_id.write({"version_ids": [(4, rec.id)]})
            self._sync_order_lines(rec.old_blanket_order_id, new_order)
            if hasattr(new_order, "message_post"):
                msg = _("New version created: %(name)s") % {"name": new_order.name}
                new_order.message_post(body=msg)
                rec.old_blanket_order_id.message_post(body=msg)
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "name": "New Version",
            "res_model": "sale.blanket.order",
            "res_id": self.new_blanket_order_id.id,
            "target": "current",
        }
