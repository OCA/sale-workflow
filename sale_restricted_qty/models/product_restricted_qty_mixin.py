# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductMinMultipleMixin(models.AbstractModel):
    _name = "product.restricted.qty.mixin"
    _description = "Product Restrict Qty Mixin"

    sale_multiple_qty = fields.Float(
        compute="_compute_sale_restricted_qty",
        store=True,
        help="Define sale multiple qty"
        " 'If not set', Odoo will"
        " use the value defined in the parent object."
        "Hierarchy is in this order :"
        "Product/product Template/product category/parent categoroies ",
        digits="Product Unit of Measure",
    )
    manual_sale_multiple_qty = fields.Float(
        string="Multiple Sale Qty", digits="Product Unit of Measure"
    )
    sale_min_qty = fields.Float(
        compute="_compute_sale_restricted_qty",
        store=True,
        help="Define sale min qty"
        " 'If not set, Odoo will"
        " use the value defined in the parent object."
        "Hierarchy is in this order :"
        "Product/product Template/product category/parent categoroies ",
        digits="Product Unit of Measure",
    )
    manual_sale_min_qty = fields.Float(
        string="Min Sale Qty", digits="Product Unit of Measure"
    )
    force_sale_min_qty = fields.Boolean(
        compute="_compute_sale_restricted_qty",
        string="Force Min Qty",
        store=True,
        help="Define if user can force sale min qty"
        " 'If not set', Odoo will"
        " use the value defined in the parent object."
        "Hierarchy is in this order :"
        "Product/product Template/product category/parent categoroies ",
    )
    manual_force_sale_min_qty = fields.Selection(
        [
            ("use_parent", "Use Parent Setting"),
            ("force", "Yes"),
            ("not_force", "No"),
        ],
        string="Manual Force Min Qty",
        required=True,
        default="use_parent",
        help="If force min qty is checked, the min quantity "
        "is only indicative value."
        "If is not test we check parent value",
    )
    sale_max_qty = fields.Float(
        compute="_compute_sale_restricted_qty",
        store=True,
        help="Define sale max qty"
        " 'If not set, Odoo will"
        " use the value defined in the parent object."
        "Hierarchy is in this order :"
        "Product/product Template/product category/parent categoroies ",
        digits="Product Unit of Measure",
    )
    manual_sale_max_qty = fields.Float(
        string="Max Sale Qty", digits="Product Unit of Measure"
    )
    force_sale_max_qty = fields.Boolean(
        compute="_compute_sale_restricted_qty",
        string="Force Max Qty",
        store=True,
        help="Define if user can force sale max qty"
        " 'If not set', Odoo will"
        " use the value defined in the parent object."
        "Hierarchy is in this order :"
        "Product/product Template/product category/parent categoroies ",
    )
    manual_force_sale_max_qty = fields.Selection(
        [
            ("use_parent", "Use Parent Setting"),
            ("force", "Yes"),
            ("not_force", "No"),
        ],
        required=True,
        default="use_parent",
        string="Manual Force Max Qty",
        help="If force max qty is checked, the max quantity "
        "is only indicative value."
        "If is not test we check parent value",
    )

    def _get_sale_restricted_qty(self):
        self.ensure_one()
        res = {
            "sale_min_qty": self.manual_sale_min_qty,
            "force_sale_min_qty": self.manual_force_sale_min_qty == "force",
            "sale_max_qty": self.manual_sale_max_qty,
            "force_sale_max_qty": self.manual_force_sale_max_qty == "force",
            "sale_multiple_qty": self.manual_sale_multiple_qty,
        }
        return res

    @api.depends(
        "manual_force_sale_min_qty",
        "manual_sale_min_qty",
        "manual_force_sale_max_qty",
        "manual_sale_max_qty",
        "manual_sale_multiple_qty",
    )
    def _compute_sale_restricted_qty(self):
        for rec in self:
            rec.update(rec._get_sale_restricted_qty())
