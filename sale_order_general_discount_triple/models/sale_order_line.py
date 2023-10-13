from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount2 = fields.Float(
        compute="_compute_discount",
        store=True,
        readonly=False,
    )
    discount3 = fields.Float(
        compute="_compute_discount",
        store=True,
        readonly=False,
    )

    @api.model
    def get_discount_vals_for_product(self, product_id, order_id):
        res = super().get_discount_vals_for_product(product_id, order_id)
        if res and "discount" in res:
            discount_field = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "sale_order_general_discount_triple.general_discount", "discount"
                )
            )
            discount_value = res["discount"]
            discount_dict = dict.fromkeys(self._discount_fields(), 0)
            discount_dict[discount_field] = discount_value
            res.update(discount_dict)
        return res
