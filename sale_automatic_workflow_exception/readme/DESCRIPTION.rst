Auto installable module for the compatibility between Sale Automatic Workflow
and Sale Exception. It ensures that orders in exception are ignored by the
cron to avoid useless testing every couple of minutes.

This module injects a domain that excludes orders with exceptions when
the automatic workflow selects orders to confirm. Note that calling confirm
on orders with exceptions is not fatal. It is just an optimalization.

Alternatively, you could manually configure the filter that selects the
orders for confirmation based on the sale order's exceptions. If you have
already done so, this module detects it and won't inject its own filter domain.
