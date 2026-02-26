Website Sale Product Multiple Quantity
=======================================

This module extends the eCommerce flow to support **Sales Multiples**
(packaging quantities) directly on the product page, in the cart,
and in the product configurator.

When a product (or variant) has a *Sales Multiple* configured,
the quantity entered by the customer on the website is automatically
rounded to a valid multiple according to the interaction type.

The rounding logic is applied dynamically when the customer:

- Opens the product page
- Changes the product variant
- Clicks the "+" (increase) button
- Clicks the "–" (decrease) button
- Manually enters a quantity
- Presses **Enter** inside the quantity input
- Changes quantities in the cart

Rounding Rules
--------------

The behavior is designed to be predictable and consistent
with packaging-based sales.

### Product Page

* On page load (or variant switch):
  - If the product is a multiple product, the default quantity is set to at least one valid multiple.
  - Otherwise, the standard minimum quantity is used.

* When clicking "+":
  - The quantity increases by one full multiple step.

* When clicking "–":
  - The quantity decreases by one full multiple step.
  - The quantity never goes below the minimum allowed value.

* When manually entering a quantity:
  - The value is rounded **UP** to the nearest valid multiple.

* When pressing **Enter**:
  - The value is processed like a manual change (no form submission).
  - Rounding logic is applied before any RPC call.

### Cart

* When clicking "+":
  - The quantity increases by one full multiple step.

* When clicking "–":
  - The quantity decreases by one full multiple step.
  - If it goes below the first multiple, it becomes ``0`` (line removal behavior).

* When manually entering a quantity:
  - The value is rounded **UP** to the nearest valid multiple.
  - ``0`` remains allowed to preserve standard cart removal behavior.

Example
-------

If a product is sold in multiples of 500:

- Entering ``1`` → becomes ``500``
- Entering ``499`` → becomes ``500``
- Entering ``501`` → becomes ``1000``
- Clicking "–" from ``500`` (product page) → becomes ``500`` (minimum)
- Clicking "–" from ``500`` (cart) → becomes ``0``
- Clicking "+" from ``0`` (cart) → becomes ``500``

Configuration
-------------

It is the responsibility of the user to configure compatible Units of Measure.

The Sales Multiple UoM must belong to the same UoM category as the product's
sales UoM. Incorrect configuration (for example, mixing unrelated UoM
categories) may lead to unexpected quantity conversions and rounding results.

The module assumes that Units of Measure are properly defined and
conversion ratios are accurate.
