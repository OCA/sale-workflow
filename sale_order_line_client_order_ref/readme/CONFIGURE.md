To display the Customer Order Reference on sale reports:

- Go to *Sales → Configuration → Settings*.
- Enable **Show Customer Order Reference in Sale Reports (PDF)**. If selected, the Order
  Ref column will be added to the lines in the sale report (PDF).

To display the Customer Order Reference on invoice reports:

- Go to *Invoicing / Accounting → Configuration → Settings*.
- Enable **Show Customer Order Reference in Invoice Reports (PDF)**. If selected, the Order
  Ref column will be added to the lines in the invoice report (PDF).

To include the Customer Order Reference in description of invoice line:

- Go to *Sales → Configuration → Settings*.
- Enable **Include Customer Order Reference in Invoice Line Description**. When enabled,
  the invoice line description will begin with the customer order reference, followed by
  a new line and the original description.
  Example:
  `[Customer Order Ref: 001]`
  `<original description>`

# Customer Order Ref Sync Policy

Configure how the **Customer Order Reference** from a Sales Order is applied to its Sales Order
Lines.

## Setup

1. **Set the company-wide default**
   - Go to **Sales → Configuration → Settings**
   - In **Sales Order Line Customer Order Ref Sync Policy**, choose the default policy to apply to all sales orders.

2. **(Optional) Set a partner-specific policy**
   - Go to **Contacts → Select a partner**
   - Open the **Sales & Purchase** tab
   - In **Sales Order Line Customer Order Ref Sync Policy**, choose the policy to apply to
     that partner. If not set, the company-wide policy will be applied to this partner’s
     sales orders.

## Customer Order Ref Policy

- **Always**: When the order value is updated, copy it to the order lines.
- **Never**: Never copy the order value to lines.
