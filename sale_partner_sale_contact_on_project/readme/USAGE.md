To use this module:

1.  Install both **Sale Partner Sale Contact** and **Sale Partner Sale
    Contact on Project**
2.  Create a sale order with a customer that has child contacts
3.  Select a **Sale Contact** from the customer's child contacts
4.  Add a service product configured to create a project or task
5.  Confirm the sale order
6.  The created project will automatically have the same sale contact
7.  You can also manually set or change the sale contact on any project
    form

The sale contact field is visible on the project form, right after the
customer field.

**Auto-switch behavior**: If you select a contact person in the customer
field and that person has a parent company, the system will
automatically:

- Set the customer field to the parent company
- Set the sale contact field to the person you selected

This behavior only applies when the restriction modules
(\*\_partner_id_company_only) are not installed.
