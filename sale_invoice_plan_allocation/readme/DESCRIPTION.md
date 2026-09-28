This module extends **sale_invoice_plan** to support invoice plan allocation by sales order line.

It adds the following Invoice Plan Methods:

- **Proportional** *(default)*

  Uses the standard behavior. Each installment invoices the same proportion of every sales order line.

- **Manual**

  Allows users to specify the quantity of each sales order line to invoice in each installment.

- **Sequential Grouped**

  Allocates one unit per line per installment and processes each group sequentially.
