# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    promotion_rule_ids = fields.Many2many(
        "sale.promotion.rule",
        string="Promotion rules",
        domain=[("rule_type", "!=", "coupon")],
    )

    coupon_promotion_rule_id = fields.Many2one(
        "sale.promotion.rule",
        string="Coupon promotion rule",
        domain=[("rule_type", "=", "coupon")],
    )
    coupon_code = fields.Char(
        related="coupon_promotion_rule_id.code", readonly=True, store=True
    )

    applied_promotion_rule_ids = fields.Many2many(
        "sale.promotion.rule",
        string="Applied Promotion rules",
        compute="_compute_applied_promotion_rule_ids",
    )

    has_promotion_rules = fields.Boolean(compute="_compute_has_promotion_rules")
    is_promotion_line = fields.Boolean(
        help="True if the line has been added by a promotion rule"
    )

    @api.depends("promotion_rule_ids", "coupon_promotion_rule_id")
    def _compute_has_promotion_rules(self):
        for rec in self:
            rec.has_promotion_rules = (
                rec.coupon_promotion_rule_id or rec.promotion_rule_ids
            )

    @api.depends("promotion_rule_ids", "coupon_promotion_rule_id")
    def _compute_applied_promotion_rule_ids(self):
        for rec in self:
            rec.applied_promotion_rule_ids = (
                rec.coupon_promotion_rule_id | rec.promotion_rule_ids
            )
