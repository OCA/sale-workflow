This module allows setting a **warehouse** on partner records and applies
a priority sequence when creating a Sale Order. If the warehouse is defined 
at a higher-priority level, it will override the lower ones. Priority are defined
following next order: `partner_shipping_id`, `partner_id` and last `user_id`.
