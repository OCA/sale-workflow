To configure this module you need to:

In sale order product recommendation you can display the product price unit
from list price or from last sale order price. To set the default value follow
the next steps

#. Go to *Sales > Configuration > Settings > Sale order recommendations*.
#. Assign the desired value to *Product recommendation price origin* field.
#. Press *Save* button to store the change.

In sale order product recommendation you can compute the recommendations using the
Delivery Address instead of the Customer. To set this option by default follow
the next steps

#. Go to *Sales > Configuration > Settings > Sale order recommendations*.
#. Assign the desired value to *Use delivery address* field.
#. Press *Save* button to store the change.

You can define other default values like as:

* Months backwards to generate recommendations.
* Number of recommendations to display.

You can force the addition of all the products recommended in the sale order. 
You can then edit the desired quantities directly in the sale order. 

#. Go to *Sales > Configuration > Settings > Sale order recommendations*.
#. Select *Force zero units included*

You can add a filter domain to exclude or include additional recommended products.

#. Go to *Sales > Configuration > Settings > Sale order recommendations*.
#. Add a filter in section *Sale order product recommendation domain* Example: ``[("product_type", "!=" "service")]``
