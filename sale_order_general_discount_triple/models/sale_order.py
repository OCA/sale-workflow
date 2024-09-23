from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("general_discount")
    def onchange_general_discount(self):
        general_discount = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_order_general_discount_triple.general_discount", "discount1"
            )
        )
        if general_discount != "no_apply":
            for record in self:
                record.order_line.update({general_discount: record.general_discount})

    def _create_delivery_line(self, carrier, price_unit):
        res = super()._create_delivery_line(carrier, price_unit)
        for line in self.order_line:
            line._compute_discount1()
            line._compute_discount2()
            line._compute_discount3()
        return res
