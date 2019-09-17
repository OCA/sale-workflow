This module allows you to combine several Sales Orders into a single invoice,
if they meet the group criteria defined by the 'Invoice Group Method'.

The group criteria is defined in the 'Invoice Group Method' by a combination
of fields of the Sales Order. 'Invoice Address', 'Currency' and 'Payment Term'
are always included.

You can assign a default 'Invoice Group Method' to customers, so that it will
be proposed on their orders.

When no Invoice Group Method is defined in a Sales Order, the standard
approach will be used, which groups by 'Invoice Address' and 'Currency'.

Note: Existing draft invoices are not considered in the process of grouping.
However, you can find the feature implemented in ``sale_merge_draft_invoice``
from sale-workflow repository.
