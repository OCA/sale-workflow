**Workflow**

- Incoming phone call directs the user to the contact form (depends on `asterisk_click2dial`).
- Click Action - Products to answer questions including pricing (depends on `partner_product_price`).
- Click the desired product.
- Click the button Bookings.
- Select the timeline view (depends on `sale_resource_booking_timeline`).
- Ctrl+Select the desired time interval for a resource combination.

A popup window will show a draft booking with these fields filled out:

- partner_id (depends on `partner_product_price`)
- type_id
- combination_id
- product_id
- start
- stop
