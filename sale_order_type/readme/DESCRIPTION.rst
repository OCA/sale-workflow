This module adds a typology for the sales orders. In each different type, you
can define: invoicing and refunding journal, a warehouse, a sequence,
the shipping policy, the invoicing policy, a payment term, a pricelist
and an incoterm.

You can see sale types as lines of business.

You are able to select a sales order type by partner so that when you add a
partner to a sales order it will get the related info to it.

Rules can also be associated with sale order types.

Inside each rule, you can select any number of products and/or product categories.

When editing a sale order that has no type, if a product matches the product of any rule then the sale order type bound to the rule is associated to the sale order.
If the rule does not match *by product*, product categories are checked.

In the sale order form you can also find the matching order type by clicking on the button *Find by rule* placed near the *Type* field.

The sale order types and the rules are inspected based on the value of their *sequence* field.
