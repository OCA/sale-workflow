Add identifications to the product
-----------------------------

1. Go to Sales -> Products -> Products
2. Create a new product
3. Go to the Sales tab and select the Required Identification option.
4. A tree will be enabled in which you must configure the required identification
   category (ies) for the product without repeating them.

   ![ADD_IDENTIFICATION](../static/img/readme/ADD_IDENTIFICATION.png)

5. If you define any category as optional, a wizard will appear when
   confirming the order to confirm whether the identifications are correct and continue with the process.
6. Save

Validate order with identification products
---------------------------------------------

1. Go to Sales -> Orders -> Quotations
2. Create a new order and add any products that require identification to the lines.
3. Once the order is confirmed, the selected customer's ID numbers will be validated to see if they have the categories
   required for the added product(s).
4. If the partner does not have all the categories in their valid identification number (Validity Date), a message will be displayed with the missing
   categories (and their message defined in the product) to validate.

   ![CATEGORY_REQUIRED](../static/img/readme/CATEGORIES_REQUIRED.png)

5. When validating the required categories, the optional ones are validated, for which a wizard will be displayed to
   confirm.

   ![CONFIRM_IDENTIFICATION](../static/img/readme/CONFIRM_IDENTIFICATION.png)

6. If the customer has all the correct identifications, then the order confirmation follows its normal flow.

