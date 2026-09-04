- Go to Sales -\> Orders -\> Quotations.
- Create a new record and fill the required fields.
- Choose a Pricelist that has a global rule configured (either by
  Category or Product).
- Click the **Recompute pricelist global** button to update prices
  according to the specified pricelist rules.
- When using **Ancestor Product Category**, the system will sum the ordered
  quantities of all products belonging to the selected ancestor category
  and all its descendants.
  If the accumulated quantity meets the rule’s minimum quantity, the
  discount will be applied to each matching order line.
- When multiple percentage-based rules apply, the system automatically
  selects the **highest discount available**, ensuring that the most
  beneficial rule is applied to the sale order.
