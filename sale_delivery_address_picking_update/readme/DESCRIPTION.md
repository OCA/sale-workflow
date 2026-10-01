When the delivery address is changed on a confirmed
sale order, Odoo's standard behaviour is to schedule a warning activity on the
pending related delivery pickings asking the user to update them manually.

This module automatically propagates the new delivery address to the pending related
pickings, without the need of scheduling an activity for it.
