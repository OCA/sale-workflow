To set quantity constraints on a product: navigate to **Sales \> Products \> Products**, open the product, and on the
**Sales** tab in the **Qty Constraints** section set corresponding values in the *Min Qty*, *Max Qty*, or
*Multiple-Of Qty* fields.

**Constraint Types:**
*   **Min Qty**: Minimum quantity required for a sale.
*   **Max Qty**: Maximum quantity allowed for a sale.
*   **Multiple-Of Qty**: Quantity must be a multiple of this value.

**Enforcement Levels (Restrict):**
For each constraint, you can choose the enforcement level:
*   **Blocking**: Strictly enforces the rule. The user cannot confirm the line with an invalid quantity.
*   **Warning**: Displays a warning (yellow/orange indication) but allows the user to proceed.
    *   *Use Case*: Use **Warning** when you want to allow flexibility, such as selling **samples** (below min qty) or clearing out **leftover stock** (remainder not matching multiple-of qty).

**Auto-Suggest:**
When you select a product in a Sales Order line, if a Minimum Quantity is strictly enforced (**Blocking**) and the current quantity is not set (or is 0/1), the system will automatically populate the quantity with the Minimum Quantity.

To set quantity constraints on a product variant: navigate to **Sales \> Products \> Product Variants**, open the
product variant, and on the **Sales** tab in the **Qty Constraints** section set corresponding values.

To set quantity constraints on a product category: navigate to **Sales \> Configuration \> Product Categories**, open
the product category, and in the **Sales Qty Constraints** section set corresponding values.

The settings are inherited from the product category to the product, and from the product to the product variant.
To override the inherited settings, check the checkbox next to the corresponding value and set the value in the product
or product variant.
