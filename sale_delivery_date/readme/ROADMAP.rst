The following modules (available in 13.0) has been merged into this module:
 - sale_warehouse_calendar
 - sale_cutoff_time_delivery
 - sale_partner_delivery_window
 - sale_partner_cutoff_delivery_window

The reason for that is that `sale_warehouse_calendar` overrides have to be
executed between `sale_cutoff_time_delivery` and `sale_partner_delivery_window`,
and there's no other clean way to do that.

However, there's still a few things to deal with:
 - Clean tests
 - Clean code
 - Use TZ where it is not the case
 - Use calendar instead of time windows when delivery preference is `working days`
