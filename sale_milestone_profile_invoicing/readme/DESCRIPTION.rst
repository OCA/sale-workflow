This module improves on sale order lines the visibility of the budget spent and invoiced for milestones products.

For this module to function properly the sale order must include one or more milestone product and one or more rate product, those products are configured as follow :

i   * A milestone product is a product of type 'Service' with a service invoicing policy set as 'Milestones' and service tracking set as 'Create a task in a new project' 
    * A rate is a product of type 'Service' with a service invoicing policy of 'Timesheets on tasks' and service tracking set as 'Don't create a task'.

For each milestone product the module changes the way the delivered and invoiced quantity is computed.

This module also adds two fields to the sale order line the 'Amount delivered from task' and 'Amount invoiced from task', they are computed for milestone products only.

Rates are linked to specific employees in the project configuration through the Invoicing tab.

The two 'Amount .. from task' fields are computed using the time logged by employee on a project in timesheets and the rate assigned to the employee.

In the detail view of a sale order line the same two fields are displayed as well their correspondant value in the company currency, it that currency is different to the sale order one.
