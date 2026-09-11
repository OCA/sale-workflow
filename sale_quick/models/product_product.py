# Copyright 2022 Camptocamp SA
# @author: Damien Crier <damien.crier@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    so_line_ids = fields.One2many(
        comodel_name="sale.order.line",
        inverse_name="product_id",
        help="Technical: used to compute quantities to sale.",
    )

    def _default_quick_uom_id(self):
        if self.env.context.get("parent_model", False) == "sale.order":
            return self.uom_id
        return super()._default_quick_uom_id()

    def _compute_process_qty_sale(self):
        so_lines = self.env["sale.order.line"].search(
            [("order_id", "=", self.env.context.get("parent_id"))]
        )
        for product in self:
            product.qty_to_process = sum(
                so_lines.filtered(lambda sol, pp=product: sol.product_id == pp).mapped(
                    "product_uom_qty"
                )
            )

    @api.depends("so_line_ids")
    def _compute_process_qty(self):
        res = super()._compute_process_qty()
        if self.env.context.get("parent_model", False) == "sale.order":
            self._compute_process_qty_sale()
        return res

    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        sale = self.env["sale.order"].browse(self.env.context.get("parent_id"))
        if self.env.context.get("in_current_parent") and sale:
            so_lines = sale.order_line
            domain = list(domain) + [("id", "in", so_lines.mapped("product_id").ids)]
        return super().search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )

    def check_access(self, operation):
        """hijack product edition rights if we're in the mass edition menu"""
        if self.env.context.get("quick_access_rights_sale"):
            return self.env["sale.order.line"].check_access(operation)
        return super().check_access(operation)
