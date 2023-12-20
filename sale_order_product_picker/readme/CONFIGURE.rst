The default behavior is to display 40 records, but it can be configured by following
these steps:

* Activate developer mode.
* Go to *Settings > Technical > Parameters > System Parameters*.
* Locate the setting with key
  "sale_order_product_picker.product_picker_limit"
  or create a new one if not exists.
* Set desired number of records
* Create ir.default with field use_delivery_address model sale.order value true if needed
