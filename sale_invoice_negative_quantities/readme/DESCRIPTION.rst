This module allows invoicing negative quantities on sales orders, when the product’s invoicing policy is set to **delivered quantities**.  
It is particularly useful for businesses that work with **returnable containers** or **returnable products** in general.

### Example use case

A delivery company may need to:

- **Deliver 4 full bottles** of a beverage product  
- **Pick up 4 empty returnable bottles** from the customer

In the sales order, the user can record:

- `+4` for the delivered full bottles  
- `-4` for the returned empty bottles

This way, it ensures **proper invoicing** of the sales order.
