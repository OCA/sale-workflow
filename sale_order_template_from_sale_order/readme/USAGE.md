Open a saved quotation or sales order and click **Create Template** in the
header, immediately after **Cancel**. The button is shown only to users with
**Template from Order** set to **Allow**, on every saved order,
including quotations, sent quotations, confirmed orders, cancelled orders and
locked orders. Type a name and click **Create**. A notification confirms that the
template was created, the wizard closes, and the screen stays on the order.
The order itself is not changed.

A sales user can change a quotation template only when they created it,
including its lines and optional products. Templates created by someone else
stay as they are. Deleting a template stays limited to sales administrators.
Any template can still be selected on a quotation.

The new template is listed with the other quotation templates. On a new
quotation, select it in **Quotation Template**. Sections, notes, product
lines and optional products are added with the quantity, unit of measure,
description, unit price and discount taken from the source order.

**Fixed Price** is set on every product line and optional product copied from
the order, including when the unit price or the discount is zero. While it
is set, applying the template uses those stored numbers. Clear **Fixed Price**
to price that line from the pricelist again. A template created by hand, with
**Fixed Price** left off, also uses the pricelist. A stored zero is not
treated as "no price" while **Fixed Price** is on.

The stored unit price is the number from the source line. It is not converted
when the new quotation uses another currency or another fiscal position.

On a line created from a fixed price:

- Changing the quantity keeps the unit price, the discount and the description.
- Changing the product recomputes the description, the unit price and the
  discount from that product and the pricelist.
- Changing only the unit of measure recomputes the unit price and the
  discount. The description stays.
- **Update Prices** recomputes the unit price and the discount from the
  pricelist.

Duplicating the sales order keeps the fixed unit price, discount and
description.

The following lines are not copied:

- Down payment lines.
- Combo products. A combo on an order is expanded into component lines, and
  the template product list does not accept combo products.
- Component lines of a combo. Their price is a share of the combo, not a
  standalone price.
