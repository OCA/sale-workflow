Click the "Create RFQ" button in the proposal form. New RFQs will be created and you
will be redirected to the RFQ list.

For each quotation an RFQ line will be created for each applicable supplier.

If there are multiple products that supplier can deliver all such products will be
grouped in one RFQ.

A vendor pricelist matches if:

- Product variant in the quotation line corresponds to the product variant in the vendor
  price list AND the quantity in the quotation line is not less than the minimum
  quantity in the vendor price list

OR

- Product variant in the quotation line corresponds to the product in the vendor price
  list AND the quantity in the quotation line is not less than the minimum quantity in
  the vendor price list

Example:

- Vendor A has a price list for the product "T-shirt" with minimum quantity 10

- Vendor B has a price list for the product variant "T-shirt color: red" with minimum
  quantity 20

- Vendor C has a price list for the product variant "T-shirt Color of shirt: blue" with
  minimum quantity 15

- Vendor D has a price list for the product variant "T-shirt color: red" with minimum
  quantity 50

A quotation has the following line: "T-shirt color: red" quantity: 30

RFQs will be created for the following vendors:

- Vendor A, because the product variant in the quotation line matches the product AND
  minimum quantity in the price list

- Vendor B, because the product variant in the quotation line matches to the product
  variant AND minimum quantity in the price list

RFQs will NOT be generated for the following vendors:

- Vendor C, because the product variant in the quotation line does not match the product
  variant in the price list

- Vendor D, because the quantity in the quotation line is less than the minimum quantity
  in the price list
