This module enhances selling timesheets in your sales order.

End-User Enhancements:
 * Usability improvements of Project > Edit > Invoicing
 * Determine Sale Order Line action on Timesheet entry
 * Usability improvements of Task related to invoicing
 * Exclude specific Task from Sale Order
 * Usability improvements of Task > Timesheets
 * Exclude specific Timesheet line from Sale Order

Technical Enhancements:
 * `account.analytic.line` extendability improvements:
   * `_timesheet_get_sale_line` overridable
 * `project.create.sale.order` extendability improvements:
   * `action_create_sale_order` refactor
