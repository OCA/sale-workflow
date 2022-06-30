To use this module, you need to:

1. Go to **Sales > Products > Products** and create a **service** product.

2. Within the product, choose your preferences under **General Information**
   tab, as follows:

   * From **Create on Order** select *Task* or *Project & Task*.
   * Tick off **Invoicing control by task** checkbox, and save.

   .. image:: static/description/product_view_invoicefinishedtask2.png

3. Go to **Sales > Orders > Orders** and create a new one. Add a customer and
   the product you have created.

4. Confirm the sales order. It will create a new task on your selected project.

5. Go to the task and you will find a smartbutton named *Not invoiceable*. When
   you click on it, you will indicate that the task can be invoiced.

   .. image:: static/description/task_view_invoicefinishedtask2.png

   If the product is configured with an invoicing policy "Timesheets on tasks",
   time spent on the task is used to compute the delivered quantity.

6. Optional: if you want to use project stages to control this, go to
   **Project > Configuration > Task Stages**, and in the stages that you
   consider are invoiceable, you have to set the *Invoiceable* field to true.
