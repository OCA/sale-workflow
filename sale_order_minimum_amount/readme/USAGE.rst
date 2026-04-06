To use this module, you need to:

#. Create a new **Sale Order**
#. Add products to the order
#. If the **Total Amount** is **less than** the configured **Minimum Allowed Sales Order Amount**:

   - A regular sales user **cannot confirm** the order
   - A **UserError** is raised:

     *"Only sale orders over X.XX can be confirmed."*
#. If the user belongs to the **Sales Manager** group:
   - The order **can be confirmed**, even if it’s below the threshold
