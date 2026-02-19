## Delivery Date Requests

A new model `sale.delivery.request` is introduced.

From a Sales Order, users can:

- Create a delivery date request using the **Request Delivery Date** button
- Track request creation datetime
- Track response datetime
- Monitor request status (draft, pending, confirmed, expired)

Each request contains multiple `sale.delivery.request.line` records,
linked to Sales Order lines.

## Partial Quantity Splitting

Each delivery request line represents a specific quantity of a sales
order line.

Users can:

- Split quantities using the **Split** button on a request line
- Assign different delivery dates per quantity block
- Merge delivery request lines back together using the **Merge** button

This allows scenarios such as:

- 2 units delivered on Date A
- 3 units delivered on Date B

## Expiration Rule

Planning confirmations are valid for a configurable number of days
(default: 15). This can be changed in **Sales > Configuration > Settings**
under the *Delivery Requests* section.

If the Sales Order is confirmed after the expiration date:

- A new priority delivery request is created automatically
- The previous confirmation is considered expired
- Stock pickings are not generated until re-confirmed

## Stock Picking Generation

Stock pickings are not created until a delivery request is confirmed.

When confirming a Sales Order:

- Delivery request lines are grouped by final promised date
- One procurement group is created per date
- One OUT picking is generated per date group

This guarantees correct logistical grouping and avoids incorrect merging
of deliveries with different delivery dates.
