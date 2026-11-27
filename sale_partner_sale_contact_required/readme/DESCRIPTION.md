This module makes the **Sale Contact** field added by
`sale_partner_sale_contact` mandatory on quotations and sale orders.

Install it when every deal must be linked to a named commercial contact
person of the customer, so that no quotation or order can be saved
without one.

Only `sale.order` is affected: invoices and vendor bills
(`account.move`) keep the sale contact optional, since the contact is
normally propagated from the originating sale order.
