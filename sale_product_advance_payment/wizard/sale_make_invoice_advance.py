from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    pdp_per_line = fields.Boolean("Deduct Down Payments per Line")

    def create_invoices(self):
        self = self.with_context(sapi_wizard_id=self.id)
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        # invoice_id = self.env['account.move'].browse(res['res_id'])
        # for move_line in invoice_id.invoice_line_ids:
        #     if len(move_line.sale_line_ids) == 1:
        #         pdpl = self.env['pdp.line'].search([('order_line_id', '=', move_line.sale_line_ids[0].id)])
        #         if len(pdpl) != 1:
        #             continue
        #         vals = {
        #             "name": "%s - Down Payment" % pdpl.order_line_id.product_id.display_name,
        #             "product_id": pdpl.pdp_id.get_dp_product().id,
        #             "quantity": -move_line.quantity,
        #             "price_unit": pdpl.price_unit*move_line.quantity,
        #             "debit": pdpl.price_unit*move_line.quantity,
        #             "credit": 0.0,
        #             "move_id": move_line.move_id.id,
        #             "account_id": move_line.account_id.id,
        #         }
        #         self.env['account.move.line'].create(vals)
        return res
