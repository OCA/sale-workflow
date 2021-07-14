# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleCouponCriteria(models.Model):
    _name = "sale.coupon.criteria"
    _description = "Coupon Multi Product Criteria"

    program_id = fields.Many2one(comodel_name="sale.coupon.program",)
    rule_min_quantity = fields.Integer(
        string="Minimum Quantity",
        compute="_compute_rule_min_quantity",
        store=True,
        readonly=False,
        help="Minimum required product quantity to get the reward",
    )
    product_ids = fields.Many2many(comodel_name="product.product", string="Products",)
    repeat_product = fields.Boolean(
        string="Repeat", help="Can product quantities count multiple times or not",
    )

    @api.depends("product_ids", "repeat_product")
    def _compute_rule_min_quantity(self):
        """Set the minimum quantity automatically to prevent errors when the rule
        isn't set to no repeat"""
        for criteria in self.filtered(lambda x: not x.repeat_product):
            criteria.rule_min_quantity = len(criteria.product_ids)

    @api.constrains("rule_min_quantity")
    def _check_rule_min_qty(self):
        for criteria in self.filtered(lambda x: not x.repeat_product):
            if len(criteria.product_ids) != criteria.rule_min_quantity:
                raise ValidationError(
                    _(
                        "The minimum quantity can't be different from the number of "
                        "products. Set the rule as repeatable to avoid this constraint."
                    )
                )
