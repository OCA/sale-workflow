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
