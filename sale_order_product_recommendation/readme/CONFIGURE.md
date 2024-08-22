To configure this module you need to:

In sale order product recommendation you can display the product price
unit from list price or from last sale order price. To set the default
value follow the next steps

1.  Go to *Sales \> Configuration \> Settings \> Sale order
    recommendations*.
2.  Assign the desired value to *Product recommendation price origin*
    field.
3.  Press *Save* button to store the change.

In sale order product recommendation you can compute the recommendations
using the Delivery Address instead of the Customer. To set this option
by default follow the next steps

1.  Go to *Sales \> Configuration \> Settings \> Sale order
    recommendations*.
2.  Assign the desired value to *Use delivery address* field.
3.  Press *Save* button to store the change.

You can define other default values like as:

- Months backwards to generate recommendations.
- Number of recommendations to display.

You can force the addition of all the products recommended in the sale
order. You can then edit the desired quantities directly in the sale
order.

1.  Go to *Sales \> Configuration \> Settings \> Sale order
    recommendations*.
2.  Select *Force zero units included*

You can add a filter domain to exclude or include additional recommended
products.

1.  Go to *Sales \> Configuration \> Settings \> Sale order
    recommendations*.
2.  Add a filter in section *Sale order product recommendation domain*
    Example: `[("product_type", "!=" "service")]`
