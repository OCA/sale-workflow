To use this module, you need to:

- Go to a sale order.
- Click on "Pay Sale Advance".
- Select the Journal and specify the amount of the advanced payment.
- "Make Advance Payment".

When generating the invoice, the system displays the advanced payments,
select those you want to add to the invoice.

**Handling Overpayments:**

By default, advance payments that exceed the invoice amount will be rejected.
To enable partial reconciliation of overpayments:

1. Go to *Settings > General Settings*
2. Scroll to the *Accounting* section
3. Check *Allow Advance Payments Exceeding Order Amount*
4. Save the settings

When enabled, advance payments larger than the order amount will be:
- Partially reconciled up to the invoice amount
- The excess amount remains as customer credit
- Useful for e-commerce integrations with tax calculation differences

**Example Scenarios:**

- **E-commerce Integration**: Customer pays $120 but Odoo calculates $100 due to tax differences
- **Prepayments**: Customer pays deposit that exceeds final invoice amount
- **Currency Fluctuations**: Payment made in different currency with rate variations
