This module extends the functionality of Sale Order to support Blanket Order and Call-off Order.

# Blanket Order

A Blanket Order is a standard sales order with the following specific features:

* Type: Classified as "Blanket Order".
* Defined Duration: Includes a validity period (end date).
* Payment Terms: Allows selection of preferred terms (e.g., 90 days end of month, upon delivery, etc.).
* Invoicing Policy: Can be based on product settings or the order itself.
* Stock Reservation: Allows advance reservation of sold quantities.
* Handling Unfulfilled Quantities: Provides options for dealing with undelivered quantities upon order expiration.
* Prices are calculated based on existing rules since it is a standard sales order type.

The blanket order serves as the central element triggering stock management and invoicing mechanisms.

## Stock Management
Delivered quantities are tracked on the sales order lines as with regular sales orders.
By default, the stock is not reserved upon confirmation of the blanket order. This is 
achieved by using the OCA module [sale_manual_delivery](https://pypi.org/project/odoo-addon-sale-manual-delivery/). As a result, the stock will be reserved only when a call-off order is created for the quantity to be delivered.

In some cases, you may want to reserve stock upon confirmation of the blanket order. This can be achieved by using the OCA module [sale_order_blanket_order_stock_prebook](https://pypi.org/project/odoo-addon-sale-order-blanket-order-stock-prebook/). This module extends the functionality of Sale Blanket Order to support the reservation of stock for future consumption by call-off orders. The reservation is done at the time of the blanket order confirmation for a consumption starting at the validity start date of the blanket order.
This behavior can be configured on the blanket order.

## Invoicing

Standard invoicing policies apply (e.g., invoice on order or on delivery). Payment terms are configurable per order. Prepayment can be enforced by configuring the invoicing policy at the order level using the OCA module [sale_invoice_policy](https://pypi.org/project/odoo-addon-sale-invoice-policy/).

## Consumption Management

A wizard will be available on the blanket order to initiate a delivery. It allows users to select products and quantities for delivery. This action creates a Call-off Order linked to the blanket order.

# Call-off Order

A Call-off Order is a standard sales order with these specific characteristics:

* Type: Classified as "Call-off Order".
* Linked to Blanket Order: Only includes products from the blanket order.
* Delivery Release: Enables the release of reserved stock for delivery.
* No Invoicing or Stock Management: These are handled via the linked blanket order.

## Stock Management

No delivery is generated directly from the call-off order.

It triggers:
* Release of the reserved quantity in the blanket order.
* Adjustment of stock reservations for the remaining quantities.


# Standard Sales Orders

To support existing workflows (e.g., e-commerce), call-off orders can be generated transparently from standard sales orders based on product and availability:

Entire orders may be converted into call-off orders if all products are linked to a blanket order.
Mixed orders split call-off items into a new call-off order, with both confirmed within the available quantities of the blanket order.
