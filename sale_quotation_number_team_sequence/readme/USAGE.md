Nothing to configure. Once both `sale_quotation_number` and
`sale_team_sale_sequence` are installed, this module is installed
automatically and takes effect on order creation:

1.  Assign a dedicated sequence to a sales team (via
    `sale_team_sale_sequence`).
2.  Create an order for that team (for example, a website order for the
    *Website Sales* team). It is numbered from the team sequence instead
    of the quotation sequence.
3.  Orders whose team has no dedicated sequence keep the standard
    `sale_quotation_number` behaviour and are assigned a quotation
    number.
