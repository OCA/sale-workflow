To use this module, follow these steps:

1.  Go to *Settings \> Sales \> Quotations & Orders*
2.  Enable the **Display sale contact on reports** option to show the
    sale contact on PDF reports (enabled by default)
3.  Go to *Sales \> Orders \> Quotations* or *Sales \> Orders \> Orders*
4.  Create or open a sale order
5.  After selecting a customer, you can select a **Sale Contact** from
    the customer's child contacts
6.  If the configuration option is enabled, the sale contact will appear
    on the printed quotation/order PDF
7.  When you create an invoice from the sale order, the sale contact
    will be automatically copied to the invoice
8.  If the configuration option is enabled, the sale contact will also
    appear on the printed invoice PDF

**Note**: Only contacts that are people (not companies) and are direct
children of the selected customer will be available for selection.

**Auto-switch behavior**: If you select a contact person in the customer
field and that person has a parent company, the system will
automatically:

- Set the customer field to the parent company
- Set the sale contact field to the person you selected

This behavior only applies when the restriction modules
(\*\_partner_id_company_only) are not installed.

**Portal access**: Portal users can always see the quotations and orders
on which they are the sale contact in *My Account \> Quotations / Sales
Orders* (read-only), in addition to the documents they can already see
through the standard portal access rules.
