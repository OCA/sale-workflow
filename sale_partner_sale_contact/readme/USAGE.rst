To use this module, follow these steps:

#. Go to *Settings > Sales > Quotations & Orders*
#. Enable the **Display sale contact on reports** option to show the sale contact on PDF reports (enabled by default)
#. Go to *Sales > Orders > Quotations* or *Sales > Orders > Orders*
#. Create or open a sale order
#. After selecting a customer, you can select a **Sale Contact** from the customer's child contacts
#. If the configuration option is enabled, the sale contact will appear on the printed quotation/order PDF
#. When you create an invoice from the sale order, the sale contact will be automatically copied to the invoice
#. If the configuration option is enabled, the sale contact will also appear on the printed invoice PDF

**Note**: Only contacts that are people (not companies) and are direct children of the selected customer will be available for selection.

**Auto-switch behavior**: If you select a contact person in the customer field and that person has a parent company, the system will automatically:

* Set the customer field to the parent company
* Set the sale contact field to the person you selected

This behavior only applies when the restriction modules (\*_partner_id_company_only) are not installed.
