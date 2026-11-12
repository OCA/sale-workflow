This module allows to make the delivery date (*commitment date*) required to
confirm a sales order.

The delivery date stays optional while the order is a quotation, so quotations
can be created, saved and edited without it. It is only checked when the
quotation is confirmed, and the confirmation is refused with an error message
when it is empty.

Since the delivery date becomes a condition to confirm the order, the module
also moves it from the *Other Info* tab to the order header, next to the other
order dates, where the salesperson can see and fill it while working on the
quotation.
