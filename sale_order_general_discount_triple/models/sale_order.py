from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("general_discount")
    def onchange_general_discount(self):
        general_discount = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_order_general_discount_triple.general_discount", "discount"
            )
        )
        if general_discount:
            for record in self:
                record.order_line.update({general_discount: record.general_discount})
