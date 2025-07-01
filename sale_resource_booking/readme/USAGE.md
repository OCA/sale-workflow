To quote one resource booking quickly, you need to:

1.  Go to *Resource bookings \> Types* and pick one.
2.  Click *Quote*.
3.  Fill the values from that wizard.
4.  Click on *Generate quotation*.

In the wizard, one of the things you need to indicate is the product.
With this module, products can be linked to resource booking types (and,
optionally, combinations). When such product is sold and the sale order
is confirmed, a new booking is created automatically (in pending state).

If you need to pre-create those pending bookings when the quotation is
not yet confirmed, you can also do that with the *Sync bookings* button
in the quotation form.

A booking can only be confirmed if its sale order is confirmed, when
there is one.

To create one of such products:

1.  Install `sale_management`.
2.  Go to *Sales \> Products \> Products*.
3.  Create one.
4.  Go to the *Sales* tab.
5.  Under *Resource Bookings*, select one *Booking type*.
6.  Optionally, select a *Resource combination* to be assigned by
    default.

When you confirm a quotation that includes some products related to
resource booking types, you will see a wizard that will help you update
quickly those bookings' values, and invite requesters to schedule them.
If you skip it, you can do it later with the bookings just created.
