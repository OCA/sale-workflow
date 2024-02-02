from odoo import fields, models


class SaleOrder(models.Model):
    _name = "sale.blanket.order"
    _inherit = ["sale.blanket.order", "base.revision"]

    current_revision_id = fields.Many2one(
        comodel_name="sale.blanket.order",
    )
    old_revision_ids = fields.One2many(
        comodel_name="sale.blanket.order",
    )

    _sql_constraints = [
        (
            "revision_unique",
            "unique(unrevisioned_name, revision_number, company_id)",
            "Order Reference and revision must be unique per Company.",
        )
    ]

    def action_view_revisions(self):
        self.ensure_one()
        result = self.env["ir.actions.actions"]._for_xml_id(
            "sale_blanket_order.act_open_blanket_order_view"
        )
        result["domain"] = ["|", ("active", "=", False), ("active", "=", True)]
        result["context"] = {
            "active_test": 0,
            "search_default_current_revision_id": self.id,
            "default_current_revision_id": self.id,
        }
        return result
