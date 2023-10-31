The default behavior is get last sales and last price from partner_id field,
but partner_delivery_address can be used by following these steps:

* Create user default value with field **use_delivery_address** of *sale.order*
  model with **true** value.
* Another option is extend view to show *use_delivery_address* field and allow that
  user select this option in each sale order.

The default behavior is to **display 40 records**, but it can be configured by
following these steps:

* Activate developer mode.
* Go to *Settings > Technical > Parameters > System Parameters*.
* Locate the setting with key
  **sale_order_product_picker.product_picker_limit**
  or create a new one if not exists.
* Set desired number of records

The default behavior is to display **qty_available**,
but it can be configured by following these steps:

* Activate developer mode.
* Go to *Settings > Technical > Parameters > System Parameters*.
* Locate the setting with key
  **sale_order_product_picker.product_available_field**
  or create a new one if not exists.
* Set desired availability field (**virtual_available**, **free_qty**)

Installation of this module sets *sale_planner_calendar.action_open_sale_order*
system parameter as **sale_order_product_picker.action_open_picker_views** to show
new picker view from sale calendar planner.
