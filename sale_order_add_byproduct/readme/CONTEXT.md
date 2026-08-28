# Business Use Case: By-product Invoicing for Contract Manufacturers

This module is designed for contract manufacturing scenarios where the client provides raw materials or a base product for processing. Unlike standard manufacturing where the output quantity of finished goods is precisely known, this use case involves a process where the exact yield of **by-products** is uncertain until after the manufacturing operation is complete.

## Scenario

A contract manufacturer processes materials supplied by a client. During this process, in addition to any primary output, a variable quantity of by-products is inevitably generated. The client is obligated to purchase these by-products from the contract manufacturer.

## Problem

At the time of sale order creation, it is impossible to accurately determine the quantity of by-products that will be produced from the manufacturing process. Therefore, these by-products cannot be initially included on the sales order for invoicing. Traditional Odoo MRP workflows are designed for planned production, not for dynamic by-product quantification for sales.

## Solution

This module automates the process of adding the actual, measured quantities of produced by-products to the corresponding sales order. Once the Manufacturing Order (MO) for the client's material is completed (marked as 'done'):

1.  The module identifies all by-products that were actually produced during that specific MO.
2.  **It filters these by-products, adding only those that are configured as "Can be Sold" (`sale_ok=True`).**
3.  It then adds these filtered by-products, along with their actual quantities, as new lines (or updates existing lines) on the original sales order linked to that MO.
4.  These by-product lines are flagged to ensure they do not trigger new manufacturing orders or procurement requests, as their supply comes directly from the completed production.

## Benefits

* **Accurate Invoicing:** Ensures clients are correctly billed for all by-products generated during the contract manufacturing process, preventing revenue loss.
* **Streamlined Operations:** Automates the manual task of reconciling by-product quantities and adding them to sales orders.
* **Improved Traceability:** Maintains a clear link between the manufacturing process and the resulting by-product sales.
* **Enhanced Reporting:** Allows for better reporting on by-product yields and sales for analysis and compliance.
