# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Dreambits Technologies Pvt. Ltd. (<http://dreambits.in>)
# Copyright 2020 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.fields import Domain


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "base.revision"]

    current_revision_id = fields.Many2one(
        comodel_name="sale.order",
    )
    old_revision_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="current_revision_id",
    )

    # Overwrite as sales.order can be multi-company
    _revision_unique = models.UniqueIndex(
        "(unrevisioned_name, revision_number, company_id)",
        message="Order Reference and revision must be unique per Company.",
    )

    def _prepare_revision_data(self, new_revision):
        vals = super()._prepare_revision_data(new_revision)
        vals.update({"state": "cancel"})
        return vals

    def action_view_revisions(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id("sale.action_orders")
        result["domain"] = Domain(["|", ("active", "=", False), ("active", "=", True)])
        result["context"] = {
            "active_test": 0,
            "search_default_current_revision_id": self.id,
            "default_current_revision_id": self.id,
        }
        return result

    def action_back_to_current(self):
        self.ensure_one()
        target_id = self.current_revision_id.id
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": target_id,
            "view_mode": "form",
            "target": "current",
        }
