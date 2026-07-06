This is a glue module that is automatically installed when both
`sale_quotation_number` and `sale_team_sale_sequence` are present.

`sale_quotation_number` gives quotations a dedicated sequence, assigning
the quotation number to every new sale order when the company is not
keeping a single enumeration. `sale_team_sale_sequence` lets each sales
team define its own sequence for the orders it creates.

Installed together, the quotation number would override the numbering of
any order belonging to a team that has its own dedicated sequence. This
module makes the team sequence authoritative for such orders: an order
whose team has a dedicated sequence is numbered from that sequence and
is not assigned a quotation number.
