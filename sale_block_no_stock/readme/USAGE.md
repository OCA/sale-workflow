To use this module, you need to:

1. Go to Settings > Sales > Quotations & Orders > Blocking sales due to lack of stock
2. Fill *Field to compare against the quantity demanded*: This field will be used to check if the quantity demanded is less than or equal to the value marked in this field. Set it to *virtual_available_at_date* for this test.
3. Fill *Groups allowed to bypass the block*: These groups will allow the blocking to be bypassed if the quantity demanded exceeds the quantity we want to check. Leave it blank to not allow any group to bypass that restriction.
4. Create a Product and set it to be storable.
5. Create a Purchase Order for the product and confirm it. Set the Picking Schedule Date on 3 days.
6. Create a Sale Order with the product and set the Commitment Date on 2 days. Confirm it and check the wizard.
7. Click on *Ajust UoM Quantity* and see the order has been modified to match forecasted quantity.
