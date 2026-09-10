This module prefixes the customer reference (`res.partner.ref`) to the
partner's `display_name` whenever it is rendered inside a Sales view —
shown as `[C00123] Acme Corp` in the customer field of a sales quotation or
order, both in the dropdown and on the selected value.

The decoration mechanism lives in the generic `partner_display_ref` module;
this module only injects the `partner_display_ref_field` context key (set to
`ref`) into the Sales views. Contacts, CRM, Invoicing and any other module that reads
`display_name` continues to see the plain partner name.
