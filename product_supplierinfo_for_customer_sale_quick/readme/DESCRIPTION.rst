Auto-installing bridge module between `product_supplierinfo_for_customer_sale` and `sale_quick`.

The flow should be: the user adds a product from `sale_quick` > the fields "customer code" and "description" 
are populated as if the same product had been added through a standard sales order line using the features of `product_supplierinfo_for_customer_sale`.
