This module automatically assigns a sales workflow at sale order creation.

The workflow to assign is selected from the `sale.workflow.process` records flagged
as *Auto assign*, using their *Auto assign domain* (evaluated against the sale order)
and ordered by priority.

It also extends the *Copy workflow on duplication* setting of
`sale_automatic_workflow` with a third option, *Copy if auto-assign finds none*:
auto-assignment runs first when a sale order is duplicated, and the origin workflow is
copied only when no workflow could be auto-assigned.
