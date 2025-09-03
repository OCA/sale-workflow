This module extends the OCA sale_automatic_workflow by automatically setting a specific route on sale order lines when orders are confirmed.

You can configure a route directly on the workflow process, and it will be applied to all lines with products delivered by stock move.

A route policy setting allows you to either replace existing routes or only fill empty ones.

The route is applied both during the onchange event for immediate visual feedback and at order confirmation.
