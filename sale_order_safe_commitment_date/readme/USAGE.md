To test the module:

- Go to *Sales > Orders* and create a new quotation.
- Set whatever customer and order lines.
- Go to the *Other info* tab, section *Delivery* and set a *Delivery date* previous to
  the expected date.
- A popup will raise warning about setting a delivery before the minimum date possible
  to promise the delivery.
- Additionally, a warning alert will be shown on the top side of the order advising the
  salesman to fix that issue.
- If the salesman ignores it, the delivery date will be set to the minimum expected date
  when the order gets confirmed.
