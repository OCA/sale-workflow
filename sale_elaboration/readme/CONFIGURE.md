To configure this module you need to:

1.  Go to *Sale \> Configuration \> Elaborations \> Sale Elaboration*.
2.  Create a new record.
3.  Set a product linked to the elaboration.
4.  If you use Multi-Step Routes, you can also select a route to procure
    this elaboration.
5.  Go to *Settings \> Inventory \> Traceability* and select *Display
    Elaboration notes on Delivery Slips* if you want to show
    elaborations on Delivery Slips or *Display Elaboration notes on
    Picking Operations* if you want to show elaborations on Picking
    Operations.

You can define elaboration profiles to limit the elaborations that can be
selected for each product.

If you want to prevent the elaboration note from being filled automatically
from the selected elaborations, set the system parameter
`sale_elaboration.auto_notes` to a falsey value in
*Settings > Technical > Parameters > System Parameters*.

To set the profile globally for a product category:

1. Go to *Inventory > Configuration > Product Categories* and choose one.
2. In the **Logistics** sections, you can set the desired **Elaboration profile**.

If you want to set an specific elaboration profile for a product:

1.  Go to *Sale \> Configuration \> Elaborations \> Sale Elaboration Profile*.
2.  Create a new record.
3.  Select the elaborations included to the profile.
4.  Set the elaboration to the related products.
