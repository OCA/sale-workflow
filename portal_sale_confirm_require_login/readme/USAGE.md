1. Send a quotation to the customer or share the portal link containing the
   access token.
2. When the customer opens the quotation from the portal:
   - If the customer is not logged in and a portal user already exists for the
     related partner, they are redirected to the login page.
   - If the customer is not logged in and no portal user exists yet, they are
     redirected to the signup page using a secure signup token.
3. After logging in or completing the signup process, the customer is redirected
   back to the quotation in the portal.
4. Before the quotation can be accepted, signed, or paid, the system checks
   that the partner linked to the sale order has all required information
   completed.
5. If required partner information is missing, the customer is prompted to
   complete it before continuing.
6. Once authentication and partner information requirements are satisfied, the
   standard Odoo confirmation, signature, and payment flow proceeds normally.
