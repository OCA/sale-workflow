Take the example of a business that relies on a primary logistics model where we fulfill orders placed through an **external e-commerce platform** or third-party reseller.

In this scenario:
1.  **Customer (`partner_id`):** The final recipient of the goods (the end-user).
2.  **Invoice Address (`partner_invoice_id`):** The external e-commerce platform/reseller responsible for payment.

The default Odoo behavior calculates the `payment_term_id` on the Sale Order based on the **Customer (`partner_id`)**. This is incorrect because our financial relationship is strictly with the reseller (the **Invoice Address**).