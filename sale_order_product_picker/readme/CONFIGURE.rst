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

When available field is **virtual_available** the default behavior is take into account
moves to commitment date or today at exactly time, but it can be configured by following
these steps:

* Activate developer mode.
* Go to *Settings > Technical > Parameters > System Parameters*.
* Locate the setting with key
  **sale_order_product_picker.product_virtual_available_time**
  or create a new one if not exists.
* Set desired time to be used in available quantities compute (Example: **23:59**)

**ATTENTION**: **product_virtual_available_time** is a technical parameter and the value must be set
in server timezone

Installation of this module sets *sale_planner_calendar.action_open_sale_order*
system parameter as **sale_order_product_picker.action_open_picker_views** to show
new picker view from sale calendar planner.

When the +1 button is used, the changes are added to a processing queue. By default, 
this queue is processed after one second, but this can be changed by using the system 
parameter **sale_order_product_picker.delay** and setting the number of seconds to 
wait before writing the lines.