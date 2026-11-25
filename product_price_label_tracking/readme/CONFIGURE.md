Go to *Sales > Configuration > Products > Label Tracking Rules* and create a rule:

- **Responsible**: the user responsible for tracking the price changes.
- **Location**: only follow products with stock on hand in this location
  or any of its children. Goods without stock tracking are ignored, unless
  **Include Non Storable** is set: they are then considered always present
  in the location. Leave empty to follow products wherever they are.
- **Pricelist**: follow the price of this pricelist. Leave empty to follow
  the sales price of the product.
- **Products**: a domain on the products to follow. Leave empty to follow
  all goods. Services and combo products are never followed.
- **Scan Every**: how often the rule is scanned. A scheduled action checks
  every hour which rules are due.

The first scan of a rule creates a label track for every product it
follows. If those products are already labelled with the current price,
select their tracks and use **Mark as Printed** instead of printing them.
