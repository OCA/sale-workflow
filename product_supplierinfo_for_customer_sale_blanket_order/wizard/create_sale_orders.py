from odoo import models


class BlanketOrderWizard(models.TransientModel):
    _inherit = "sale.blanket.order.wizard"

    def _prepare_so_line_vals(self, line):
        res = super()._prepare_so_line_vals(line)
        product_customer_reference = line.blanket_line_id.product_customer_reference
        if product_customer_reference:
            res.update({"name": product_customer_reference})
        return res
