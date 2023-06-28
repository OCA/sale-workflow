from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        for rec in self:
            if rec.product_id and rec.product_id.product_tmpl_id.sale_uom_id:
                rec.product_uom = rec.product_id.product_tmpl_id.sale_uom_id

        return res

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        res = super(SaleOrderLine, self).product_uom_change()
        if (
            self.product_id.list_price_base_sale_uom
            and self.product_id.product_tmpl_id.sale_uom_id
            and self.product_id.product_tmpl_id.sale_uom_id
            != self.product_id.product_tmpl_id.uom_id
        ):
            if self.product_id.product_tmpl_id.sale_uom_id.uom_type == "bigger":
                factorUom = 1 / self.product_id.product_tmpl_id.sale_uom_id.factor_inv
            else:
                factorUom = self.product_id.product_tmpl_id.sale_uom_id.factor
            self.price_unit = self.price_unit * factorUom
        return res
