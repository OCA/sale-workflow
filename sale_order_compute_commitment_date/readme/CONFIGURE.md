To configure this module, you need to:

- Create a product.
- Set its delay time on the "Inventory" tab.
- If you want product variants to increase the commitment date, check the Attribute Extend Lead Time boolean.
- Now configure a variant for the product and set its lead time.
- Create a sales order and add the product.
- On the "Other Information" tab you will see the commitment date its automatically computed.
- This module relies on the resource calendar to calculate dates, including both working days and any configured leave days.
- Once the sale order is confirmed, it computes again the commitment date.