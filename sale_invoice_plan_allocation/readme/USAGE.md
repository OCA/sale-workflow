1. Open a quotation, tick **Use Invoice Plan**, and choose an **Invoice Plan
   Method** (*Proportional*, *Sequential Grouped*, or *Manual*).
2. For *Sequential Grouped*, set an **Invoice Plan Group** number on each order
   line so the lines you want invoiced together share the same number.
3. Click **⇒ Create Invoice Plan** and fill in the start date and interval. For
   *Sequential Grouped* the **Number of Installments** is computed from the
   order lines and shown read-only.
4. Review or adjust the allocations:
   - **Allocate** opens one installment; **⇒ Edit Line Allocations** opens them
     all in a single list.
   - With *Manual*, **⇒ Split Remaining Quantities Evenly** fills every open
     installment as a starting point.
   - A row turns red when a line is over-allocated; an installment turns red
     when its allocated amount does not match its target.
5. Confirm the order, then click **Create Invoice by Plan** to issue the next
   invoice or all remaining invoices.

With *Manual*, an even split may leave a fraction of a unit on the last installment when the ordered quantity is not divisible by the number of installments. The **Balance** column shows it before confirmation.
