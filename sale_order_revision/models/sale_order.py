# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Dreambits Technologies Pvt. Ltd. (<http://dreambits.in>)
# Copyright 2020 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "base.revision"]

    current_revision_id = fields.Many2one(
        comodel_name="sale.order",
    )
    old_revision_ids = fields.One2many(
        comodel_name="sale.order",
    )

    # Overwrite as sales.order can be multi-company
    _sql_constraints = [
        (
            "revision_unique",
            "unique(unrevisioned_name, revision_number, company_id)",
            "Order Reference and revision must be unique per Company.",
        )
    ]

    def _prepare_revision_data(self, new_revision):
        vals = super()._prepare_revision_data(new_revision)
        vals.update({"state": "cancel"})
        return vals

    def action_view_revisions(self):
        self.ensure_one()
        result = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        result["domain"] = ["|", ("active", "=", False), ("active", "=", True)]
        result["context"] = {
            "active_test": 0,
            "search_default_current_revision_id": self.id,
            "default_current_revision_id": self.id,
        }
        return result

    def create_revision(self):
        # Extends base_revision module
        action = super().create_revision()
        # Keep links to Invoices on the new Sale Order
        old_lines = self.order_line
        new_lines = self.current_revision_id.order_line
        for old_line, new_line in zip(old_lines, new_lines):
            new_line.invoice_lines = old_line.invoice_lines
        return action

    def action_cancel_create_revision(self):
        for sale in self:
            sale.action_cancel()
            action = sale.create_revision()
        if len(self) == 1:
            return action
        return {}
