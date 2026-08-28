This module brings the multi-discount distribution introduced by
``account_multi_discount`` to the *Sales* module.

It adds the ``discount_distribution`` JSON field on ``sale.order.line``,
recomputes the legacy ``discount`` aggregate from it, registers the OWL
widget on the sale order form/list views, propagates the distribution to
the generated invoice line on invoicing, and renders the individual
discounts in the printable sale order report.