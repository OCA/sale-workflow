# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderAddCoupon(models.TransientModel):

    _name = "sale.order.add.coupon"
    _description = "Sale Order Add Coupon"

    name = fields.Char(required=True)

    def doit(self):
        so = self.env["sale.order"].browse(self.env.context["active_id"])
        so.add_coupon(self.name)
        return True
