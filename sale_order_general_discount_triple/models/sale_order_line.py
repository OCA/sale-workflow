from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount2 = fields.Float(compute="_compute_discount2", store=True, readonly=False)
    discount3 = fields.Float(compute="_compute_discount3", store=True, readonly=False)

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_discount(self):
        general_discount = self._get_discount_field_position("general_discount")
        if "discount" != general_discount:
            self.update({"discount": 0.0})
            return
        for line in self:
            if general_discount == "discount":
                line.update({"discount": line.order_id.partner_id.sale_discount})
        return

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_discount2(self):
        general_discount = self._get_discount_field_position("general_discount")
        if "discount2" != general_discount:
            self.update({"discount2": 0.0})
            return
        for line in self:
            if general_discount == "discount2":
                line.update({"discount2": line.order_id.partner_id.sale_discount})

    @api.depends("product_id", "product_uom", "product_uqom_qty")
    def _compute_discount3(self):
        general_discount = self._get_discount_field_position("general_discount")
        if "discount3" != general_discount:
            self.update({"discount3": 0.0})
            return
        for line in self:
            if general_discount == "discount3":
                line.update({"discount3": line.order_id.partner_id.sale_discount})


    def _get_discount_field_position(self, field_name):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_order_general_discount_triple.{}".format(field_name), "discount"
            )
        )
