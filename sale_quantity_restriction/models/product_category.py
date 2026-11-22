# Copyright 2025 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    manual_quantity_restriction_id = fields.Many2one(
        "sale.quantity.restriction",
        string="Manual Quantity Restriction",
        help="Allows to override the Parent Quantity Restriction defined in the "
        "product's category",
    )

    parent_quantity_restriction_id = fields.Many2one(
        "sale.quantity.restriction",
        string="Parent Quantity Restriction",
        related="parent_id.quantity_restriction_id",
    )

    quantity_restriction_id = fields.Many2one(
        "sale.quantity.restriction", compute="_compute_quantity_restriction_id"
    )

    @api.depends("parent_quantity_restriction_id", "manual_quantity_restriction_id")
    def _compute_quantity_restriction_id(self):
        for rec in self:
            rec.quantity_restriction_id = (
                rec.manual_quantity_restriction_id or rec.parent_quantity_restriction_id
            )
