Sale Order Line

- Untaxed invoices amount
    Compute the untaxed amount already invoiced from the sale order line, taking the refund attached
            the so line into account. This amount is computed as
                SUM(inv_line.price_subtotal) - SUM(ref_line.price_subtotal)
            where
                inv_line is a customer invoice line linked to the SO line
                ref_line is a customer credit note (refund) line linked to the SO line

- Untaxed amount to invoice
    Total of remaining amount to invoice on the sale order line (taxes excl.) as
            total_sol - amount already invoiced
            where Total_sol depends on the invoice policy of the product.
            Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
            come only from the SO lines.

Sale Order
    Compute the total untaxed amount to invoice of the SO:
        This amount is computed as

- Untaxed amount to invoice
    sum(order.order_line.mapped("untaxed_amount_to_invoice"))

- Untaxed invoices amount
    sum(order.order_line.mapped("untaxed_amount_invoiced"))
