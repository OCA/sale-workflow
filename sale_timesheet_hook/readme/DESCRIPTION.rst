This module adds hook points in ``sale_timesheets`` module in order to add more
flexibility in the billing types for the creation of *Sale Orders*.

Although the original code has been modified a bit, the logic has been
respected and the method still does exactly the same.

Technical Enhancements:
 * `account.analytic.line` extendability improvements:
   * `_get_valid_so_line_ids` overridable
 * `project.create.sale.order` extendability improvements:
   * `action_create_sale_order` refactor, reported in `odoo/odoo#31047 <https://github.com/odoo/odoo/pull/31047>`_.
