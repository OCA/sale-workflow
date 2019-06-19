To use this module, you need to:

1. Go to Sales -> Product and create a service product

2. In the product go to Sales tab > Invoicing section and select
   (1) An invocing policy (2) Track service must be create a task and
   tack hours (3) Set 'Invoicing control by task' checkbox and save


   .. image:: static/description/product_view_invoicefinishedtask.png


3. Go to Sales -> Sale orders -> Create a new one. Add a customer and the
   product you have created
4. Confirm the sales order, it will create you a project and a task
5. Go to the task and you will find a smartbutton called Not invoiceable, when
   you press the button you will indicate that the task can be invoiced

   .. image:: static/description/task_view_invoicefinishedtask.png

   If the product is configured with an invoicing policy = Order, then the
   delivered quantity is set to the ordered quantity. Otherwise, the time spent
   on the task is used.

6. Optional: if you want to use project stages to control this Go To
   Project -> Configuration -> Stages -> You have to set true the field
   Invoiceable in the stages that you consider are invoiceable. Event to use
   stages for this functionality you can also set it manually in the task
   whenever you want.
