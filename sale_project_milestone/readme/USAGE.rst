Creating Projects with Milestones
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create a sale order with a product configured for "Project & Milestone"
2. In the sale order line:

   * **Option A**: Leave both **Project** and **Existing Milestone** fields empty to create a new project automatically
   * **Option B**: Select an existing **Project** to add a new milestone there
   * **Option C**: Select an existing **Project** and **Existing Milestone** to link them directly

3. Confirm the sale order
4. The system will:

   * Create a new project (using the project template if configured) OR use the selected project
   * Create a new milestone in that project OR link the selected existing milestone
   * Link the milestone to the sale order line

Using Project Templates
~~~~~~~~~~~~~~~~~~~~~~~

If a **Project Template** is configured on the product:

1. When leaving the **Project** field empty on the sale order line
2. The system will duplicate the template project
3. All template tasks and settings will be copied to the new project
4. A milestone will be created in the new project

Linking Existing Milestones to Confirmed Sale Orders
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For already confirmed sale orders where you need to link an existing milestone:

1. Open a confirmed sale order (in 'sale' state)
2. Edit a sale order line with milestone tracking
3. Select an **Existing Project** and **Existing Milestone**
4. Click the **"Link Milestone"** button in the order line
5. The milestone will be linked to the sale order line
6. If invoices already exist, their analytic lines will be automatically registered on the project's analytic account

**Note**: The **Existing Project** and **Existing Milestone** fields stay editable in quotation, and in confirmed state only while no project has yet been linked to the line. Once a project is linked (either auto-created at confirmation, or via the **Link Milestone** button), the fields become read-only and display the actual link. They are also read-only when the order is locked or cancelled.

Milestone-Based Invoicing
~~~~~~~~~~~~~~~~~~~~~~~~~

When the service policy is "Based on Milestones":

1. Mark the milestone as reached in the project
2. The delivered quantity on the sale order line will be updated
3. Create an invoice from the sale order
4. The invoice lines will automatically have the correct analytic distribution
