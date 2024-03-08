from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    untaxed_amount_invoiced = fields.Monetary(
        string="Untaxed Invoiced Amount",
        compute='_compute_untaxed_amount_invoiced',
        compute_sudo=True, store=True
    )
    untaxed_amount_to_invoice = fields.Monetary(
        string="Untaxed Amount To Invoice",
        compute='_compute_untaxed_amount_to_invoice',
        compute_sudo=True,
        store=True
    )

    @api.depends('invoice_lines',
                 'invoice_lines.price_total',
                 'invoice_lines.invoice_id.state',
                 'invoice_lines.invoice_id.type')
    def _compute_untaxed_amount_invoiced(self):
        """ Compute the untaxed amount already invoiced from the sale order line,
         taking the refund attached the so line into account. This amount is computed as
                SUM(inv_line.price_subtotal) - SUM(ref_line.price_subtotal)
            where
                `inv_line` is a customer invoice line linked to the SO line
                `ref_line` is a customer credit note (refund) line linked to the SO line
        """
        for line in self:
            amount_invoiced = 0
            for invoice_line in line.invoice_lines:
                invoice_id = invoice_line.invoice_id
                if invoice_id.state in ['open', 'in_payment', 'paid']:
                    invoice_date = invoice_id.date_invoice or fields.Date.today()
                    if invoice_id.type == 'out_invoice':
                        amount_invoiced += invoice_line.currency_id.with_context(
                            {'date': invoice_date}).compute(
                            invoice_line.price_subtotal,
                            line.currency_id,
                            line.company_id)

                    elif invoice_id.type == 'out_refund':
                        amount_invoiced -= invoice_line.currency_id.with_context(
                            {'date': invoice_date}).compute(
                            invoice_line.price_subtotal,
                            line.currency_id,
                            line.company_id)
            line.untaxed_amount_invoiced = amount_invoiced

    @api.depends('state', 'price_reduce', 'product_id',
                 'untaxed_amount_invoiced', 'qty_delivered')
    def _compute_untaxed_amount_to_invoice(self):
        """ Total of remaining amount to invoice on the sale order line (taxes excl.) as
                total_sol - amount already invoiced
            where Total_sol depends on the invoice policy of the product.
            Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
            come only from the SO lines.
        """
        for line in self:
            amount_to_invoice = 0.0
            if line.state in ['sale', 'done']:
                price_subtotal = 0.0
                uom_qty_to_consider = line.qty_delivered \
                    if line.product_id.invoice_policy == 'delivery' \
                    else line.product_uom_qty
                price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                price_subtotal = price_reduce * uom_qty_to_consider
                if len(line.tax_id.filtered(lambda tax: tax.price_include)) > 0:
                    price_subtotal = line.tax_id.compute_all(
                        price_reduce,
                        currency=line.order_id.currency_id,
                        quantity=uom_qty_to_consider,
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id)['total_excluded']

                amount_to_invoice = price_subtotal - line.untaxed_amount_invoiced
            line.untaxed_amount_to_invoice = amount_to_invoice
