# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_type = fields.Many2one(
        comodel_name="sale.order.type", string="Sale Order Type", company_dependent=True
    )

    @api.model
    def fix_hook(self):

        # Ensure each company has at least one sale.order.type record
        for company in self.env["res.company"].search([]):
            if not self.env["sale.order.type"].search(
                [("company_id", "=", company.id)]
            ):
                self.env["sale.order.type"].create(
                    {"name": "Normal Order", "company_id": company.id}
                )

        # Ensure each SO has filled the type_id, according to the sale order company
        sale_order_ids = self.env["sale.order"].search([("state", "!=", "draft")])
        for _so in sale_order_ids:
            _so.type_id = self.env["sale.order.type"].search(
                [("company_id", "in", [_so.company_id.id, False])], limit=1
            )
