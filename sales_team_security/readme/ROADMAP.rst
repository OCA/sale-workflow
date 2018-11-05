* For restricting partners access, you have to disable or edit the existing
  rule "res.partner.rule.private.employee" to something similar to:

  .. code-block:: python

    [('message_follower_ids', 'in', user.partner_id.ids),
    '|', ('type', '!=', 'private'), ('type', '=', False)]

* This module modifies sales security groups hierarchy, so any other module
  doing something similar might conflict with this one.
* This module is designed for supporting only sales part, so someone that has
  access to other Odoo parts (for example, an accountant), shouldn't have this
  new permission, or some access errors will be found when seeing invoices and
  other documents. A `sales_team_security_account` bridge module can be done
  for fixing this case, but not in the case of other parts like warehouse.
* Split the module in 2 as now `crm` is independent.
