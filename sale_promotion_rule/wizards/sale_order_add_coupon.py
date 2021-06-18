# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderAddCoupon(models.TransientModel):
    _name = "sale.order.add.coupon"
    _description = "Wizard to add coupon to a sale order"

    name = fields.Char(required=True)

    @api.multi
    def doit(self):
        so = self.env["sale.order"].browse(self.env.context["active_id"])
        so.add_coupon(self.name)
        return True
