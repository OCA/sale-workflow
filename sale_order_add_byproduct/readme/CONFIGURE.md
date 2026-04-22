No specific configuration is required for this module to function, beyond the standard Odoo setup for Manufacturing Orders, Bills of Materials (BOMs), and Products.

However, for optimal use:

* **By-product Products**: Ensure your by-product products are correctly defined in Odoo, ideally belonging to a specific product category (e.g., 'By-products').
    * **Crucially, the by-product product *must* have its "Can be Sold" (`sale_ok`) field set to `True`** in its product form under the "Sales" tab. By-products with `sale_ok = False` will be ignored by this module and will not be added to the Sales Order.
* **BOMs with By-products**: Your Bills of Materials (BOMs) for your main manufactured products must have the relevant by-products configured under the "By-products" tab with their planned quantities.
