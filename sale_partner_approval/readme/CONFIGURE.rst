The Sales Order validation rules are configurable.
By default Sale Order confirmation is prevented is the Customer or Invoice Address
is not approvaed to be used in sales.

To configure Sales Order validations navigate to
Sales / Configuration / Sales Orders / Sale Exception Rules.
You need to belong to the Exception Manager security group to see this menu option.

For new customer to require approval before being sold to, configure the Contact Stages
appropriately. For example:

* Navigate to Contacts / Configuration / Contact Stages
* Edit the "Active" stage: uncheck "Default Stage" and check "Approved for Sales"
* Edit the "Draft" stage: check "Default Stage" and uncheck "Approved for Sales"
