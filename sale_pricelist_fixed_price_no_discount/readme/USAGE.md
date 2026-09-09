1. Configure a pricelist rule with *Compute Price* set to *Fixed Price*.
2. Create or edit a quotation using that pricelist.
3. Add a product matching the fixed-price pricelist rule.

On the matching sale order line, the discount field is readonly. 
If a discount is set through an import, RPC call, or custom code, 
the sale order line is rejected with a validation error.
