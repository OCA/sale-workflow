To use this module:

#. Go to **Sales > Products > Products** and open a product.
#. In the **Sales** tab, enable **Semaphore**.
#. Define the allowed discount percentages for the three thresholds:

   * **Discount Success**: upper band for a green result.
   * **Discount Warning**: upper band for a yellow result.
   * **Discount Danger**: final accepted limit.

#. Optionally, configure the same values on the product category to provide
   default thresholds for all products in that category.

Once configured, the semaphore is evaluated automatically on each sales order
line according to the effective unit price:

* **Green** when the price stays above the success threshold.
* **Yellow** when the price falls below the success threshold but remains above
  the warning threshold.
* **Red** when the price falls below the warning threshold.

Additional behavior:

* The line is highlighted when the price goes below the **danger** threshold.
* The semaphore value is copied to invoice lines.
* Non-manager users are prevented from confirming or updating confirmed sales
  orders when the effective price is below both the configured semaphore limit
  and the applicable pricelist price.
* Product-level settings take precedence over category-level settings.
