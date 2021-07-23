# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_reward_values_product(self, program):
        """Add the link to the program in the discount line"""
        res = super()._get_reward_values_product(program)
        res["coupon_program_id"] = program.id
        return res

    def _get_reward_values_discount(self, program):
        """Add the link to the program in the discount line"""
        res = super()._get_reward_values_discount(program)
        # The original method returns a dict.values(), which is weird:
        # https://git.io/J88As
        vals = [r for r in res][0]
        vals["coupon_program_id"] = program.id
        return {"x": vals}.values()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    coupon_program_id = fields.Many2one(
        comodel_name="sale.coupon.program",
        ondelete="restrict",
        string="Coupon Program",
    )
