If we want to use certain product in the Sales catalog with the sencondary unit
we need to set a default secondary unit for sales in product form.

Product with a dependent default secondary unit:
- The catalog displays quantities in the secondary unit.
- Quantities entered in the catalog are interpreted as secondary units and
  converted to primary units before being saved to the order line.
- If the order line does not yet have a secondary unit assigned, it is
  automatically set to the product's default one.

Product with an independent default secondary unit, or no secondary unit:
- The catalog operates with the primary unit (standard behavior).
