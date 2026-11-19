## Sales Order Effective Delivery Date
This module extends the Odoo sales order list and search view with the existing effective delivery date.

### Features
* Display the effective delivery date in the sales order list, with the option to show or hide the column.
* Search sales orders by effective delivery date.
* Filter sales orders that have an effective delivery date.
* Filter sales orders that do not have an effective delivery date.
* Filter sales orders by a specific effective delivery date or date range.
* Group sales orders by effective delivery date.

**Note:** The module uses the standard Odoo `effective_date` field and does not modify how the date is computed. 
The effective delivery date is based on the first completed customer delivery.