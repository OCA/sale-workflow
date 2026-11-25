This module works by overriding the ``domain`` of three core window
actions (``sale.action_quotations_with_onboarding``,
``account.action_move_out_invoice_type`` and
``account.action_move_out_refund_type``). Overriding a field on an
existing record via XML replaces its value rather than merging it, so if
a future Odoo release, or another installed module, changes the base
domain of one of these actions, this module's override will silently
take precedence and any new base condition will be lost. Re-check these
domains against the ``sale``/``account`` modules whenever upgrading.

The **Sales > Orders > Orders** list (``sale.action_orders``) is not
covered by this module and may still show cancelled orders, depending on
your Odoo 18 setup.
