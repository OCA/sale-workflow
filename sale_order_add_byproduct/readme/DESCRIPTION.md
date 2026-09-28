This module extends the functionality of Manufacturing Orders to automatically transfer produced by-products to the associated Sale Order once the Manufacturing Order is closed. This allows for easier invoicing and management of by-products sold to customers.

## Key Features
* Automatically adds/updates Sale Order Lines for by-products when a Manufacturing Order is marked as 'done'.
* Prevents additional Manufacturing Orders or procurements from being triggered for these by-product lines, as they are a result of existing production.
* Ensures accurate tracking of by-product quantities on the Sale Order for invoicing purposes.
