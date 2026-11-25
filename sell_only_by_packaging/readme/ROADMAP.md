### Product Catalog Integration

Products configured with **Sell only by packaging** cannot currently be added directly from the sales product catalog, as the catalog does not allow selecting a packaging before creating the sale order line.

Consider adapting the product catalog in a future improvement to support packaging selection and quantity increments based on the selected packaging.

### Product Variants Validation

When **Sell only by packaging** is enabled, the existing validation checks whether sellable packaging is available. However, creating new product variants afterward may result in variants without packaging configured for sales.

Consider improving the validation to check each active variant individually and detect missing sales packaging when variants are created or modified.

### External Sales Integrations

External tools that create sale order lines directly, such as e-commerce connectors, Excel imports, or the `sale_order_product_recommendation` wizard, may encounter validation errors when products require packaging and no valid packaging is provided.

Consider improving packaging selection and quantity handling when creating sale order lines through external integrations, potentially allowing automatic packaging assignment and quantity adjustment to valid packaging multiples.
