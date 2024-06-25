This module extends the functionality of the Sales module to restrict users from updating the quantity of products in sale order lines:

- When the sale order is locked/confirmed, users are still able to adjust the quantities.
- This becomes a problem if the related pickings are already (or partially) released, as it generates a return operation.
- The module ensures that once a sale order is (at least partially) sent to WMS, the quantities cannot be edited, preventing users from mistakenly thinking they can still impact quantities to deliver.
