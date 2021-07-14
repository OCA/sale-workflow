To configure multiple product criterias:

#. Go to *Sales > Catalog > Coupon Programs* and select or create a new one.
#. On the *Coupon Criteria* field choose *Multi Product*.
#. The standard domain will be hidden and a criteria list will be shown.
#. Add as many criterias as needed for the desired promotion behavior.

In the list of criterias we can configure:

- Qty: The minimum quantity of products in the sale order to fulfill the condition.
- Products: The products that should be present to fulfill the condition.
- Repeat: The sum of quantities of any product in the criteria must be at least the one
  defined in the minimum quantities. If not set, the minimum quantity will be the number
  of products defined in the criteria, as all of them must be in the order to fulfill
  the condition.

Some examples:

 ===== ================ ========
  Qty      Products      Repeat
 ===== ================ ========
    1   Prod A
 ===== ================ ========

A unit of Product A must be in the sale order.

 ===== ================ ========
  Qty      Products      Repeat
 ===== ================ ========
    2   Prod B, Prod C
 ===== ================ ========

A unit of Product B and Product C must be in the sale order.

 ===== ================ ========
  Qty      Products      Repeat
 ===== ================ ========
    3   Prod D, Prod E   X
 ===== ================ ========

Either Product D or Product E or both must be in the sale order and the sum of their
quantities must be three.

Also note that all the defined criterias must be fulfilled or the program won't be
applied.
