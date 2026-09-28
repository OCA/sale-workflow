To use this module:

#. Install both **Sale Partner Sale Contact** and **Sale Partner Sale Contact on Project**
#. Create a sale order with a customer that has child contacts
#. Select a **Sale Contact** from the customer's child contacts
#. Add a service product configured to create a project or task
#. Confirm the sale order
#. The created project will automatically have the same sale contact
#. You can also manually set or change the sale contact on any project form

The sale contact field is visible on the project form, right after the customer field.

**Auto-switch behavior**: If you select a contact person in the customer field and that person has a parent company, the system will automatically:

* Set the customer field to the parent company
* Set the sale contact field to the person you selected

This behavior only applies when the restriction modules (\*_partner_id_company_only) are not installed.
