1.  **Create a Sales Order (SO)** for the main product that your client will receive.
    * The main product should have a Bill of Materials (BOM) defined that includes the by-products under its "By-products" tab.
    * The main product's inventory route should be configured for "Manufacture" (or "Make to Order" if applicable).
2.  **Confirm the Sales Order**. This will automatically generate a Manufacturing Order (MO) for the main product.
3.  **Process the Manufacturing Order**:
    * Navigate to the generated Manufacturing Order.
    * Ensure all necessary raw materials are available.
    * Move the MO through its production stages (e.g., confirm, plan, start production, consume components).
    * **Crucially, ensure the actual quantities produced for the by-products are recorded** on the MO's respective moves (e.g., on the `stock.move` records associated with the by-products, typically under the 'Finished Products' or 'By-products' tab of the MO, the 'Done' quantity should reflect the actual yield).
4.  **Mark the Manufacturing Order as Done**. This is the trigger for the module's automation.
5.  **Verify the Sales Order**:
    * Go back to the Sales Order that was linked to the completed MO.
    * You will find new line(s) added (or existing lines updated) for the by-product(s) with their actual produced quantities from the MO.
    * These by-product lines will be flagged internally (`is_mrp_byproduct_line = True`) to prevent them from triggering new, unnecessary manufacturing orders or procurement requests.
6.  **Invoice the Client**: You can now proceed to create an invoice from the Sales Order, which will include the by-products for billing to your client.

This automated process ensures that clients are accurately billed for all by-products generated during the contract manufacturing process.
