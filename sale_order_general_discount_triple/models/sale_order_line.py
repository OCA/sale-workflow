from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
        compute=False,
        store=True,
        readonly=False,
        default=0.0,
    )

    @api.model
    def default_get(self, fields):
        vals = super(SaleOrderLine, self).default_get(fields)
        general_discount = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_order_general_discount_triple.general_discount", "discount"
            )
        )
        value = vals.get("discount") or 0.0
        vals.update(
            {
                "discount": 0.0,
                "discount2": 0.0,
                "discount3": 0.0,
            }
        )

        vals.update(
            {
                general_discount: value,
            }
        )
        return vals

    @api.model
    def create(self, vals):
        sale_order = self.env["sale.order"].browse(vals["order_id"])
        general_discount = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_order_general_discount_triple.general_discount", "discount"
            )
        )
        if general_discount:
            vals[general_discount] = sale_order.general_discount
        return super().create(vals)
