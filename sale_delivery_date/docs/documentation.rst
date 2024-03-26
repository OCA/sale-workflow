How it works
============

Different usecases
------------------

There's two different cases

    * sale order with a commitment_date

      "commitment_date" is copied to the picking's "date_deadline" field, and the "scheduled_date" is computed from it.

    * sale order without a commitment_date

      picking's "date_deadline" (which should be the same as order's "planned_date") is computed based on the "date_order" field once it is confirmed, and "now()" otherwise.


Those two "date_deadline" and "scheduled_date" are computed in two steps:

    * "date_deadline" is computed based on order's "date_order" (if not "commitment_date" is set)
    * "scheduled_date" is computed based on move's "scheduled_date", since all products have their own delay


Note
----

Depending on the picking/order delivery strategy, "date_deadline" and "scheduled_date" are computed differently.

    * if strategy = ASAP, picking's "date_deadline" is the earliest "date_deadline" among its stock moves (same principle applies for sale_order date_planned and picking scheduled date)
    * if strategy = all at once, picking's "date_deadline" is the latest "date_deadline" among its stock moves.


vocabulary used in the following
--------------------------------

* sale_delay (customer_lead): set on the product, represents the delay between order confirmation and the delivery.
* security_lead: set on the company, represents the delay between expedition and reception of the goods (set to 1 day)
* workload: preparation delay, computed as customer_lead and security lead)

The workflow

Here's the detailed process that describes how delivery dates are computed.
As explained above, those dates are computed at sale_order_line level, since delays are configured on the product.


    #. Retrieves date_order / confirmation_datetime
    #. postpone to next cutoff

       postpone to tomorrow at cutoff time if date_order is after today's cutoff, postpone to today's cutoff otherwise

       /!\\ customer's might have their own cutoff

    #. postpone to a working day

       previously computed date might be in a non-working day (I.E. date_order is after friday's cutoff, then date_order with cutoff is saturday at cutoff time)

       In such case, postpone this to monday.

    #. Add the workload.

       The previously computed date should be postponed to the end of the current attendance.

       I.E. :

       * monday at 09:00 → monday at 12:30
       * monday at 13:00 → monday at 17:30

       (according to "Standard 40 hours/week" calendar)

    #. Add the security lead, which is considered as the delivery lead time (1 day)

       - monday at 17:30 → tuesday at 17:30

       but only the date is used for the next of the process, as it is up to the carried to manage the delivery time.

    #. apply delivery preference (time windows)

       tuesday:

         * anytime : delivery_date = tuesday
         * working days: delivery_date = tuesday
         * friday window: delivery_date = friday

Here, we now have the order.planned_date / picking.date_deadline.

The idea here is that the step 6) might have postponed the delivery by a few days, and we want to start working on the order as late as possible.

In the "6) friday window" case, order was ready on tuesday, which is too early.


    #. deduct security lead from the delivery date

       (order.planned_date / picking.date_deadline) (time doesnt matter here, we use 23:59:59 to be inclusive)

       I.E. Friday → Thursday

    #. Find the latest possible end of working day

       * Thursday → Thursday at 17:30
       * Saturday → Friday at 17:30

    #. Deduct the workload (should be 1 working day in most cases)

       Friday at 17:30 → Friday at 13:00

    #. Apply once again the cutoff

       Friday at 13:00 → Friday at 09:00


Example
-------

Here's a simple case:
* date_order monday at 10:00
* cutoff = 9:00
* customer delivery_preference = fridays between 8 and 16
* product.sale_delay = 1d  ==

    #. date_order: monday at 10:00
    #. postpone to cutoff: monday at 10:00 → tuesday at 09:00
    #. postpone to working day: tuesday at 09:00 → tuesday at 09:00
    #. add workload: tuesday at 09:00 → tuesday at 12:30
    #. add security lead: tuesday at 12:30 → wednesday at 12:30
    #. apply delivery preference: wednesday at 12:30 → friday at 08:00 (date_deadline)
    #. deduct security_lead : friday at 08:00 → Thursday at 23:59:59
    #. latest end of attendance: Tursday at 23:59:59 → Thursday at 17:30
    #. deduct workload: Thursday at 17:30 → Thursday at 13:00
    #. apply cutoff: Tursday at 13:00 → Thursday at 09:00 (scheduled_date).
