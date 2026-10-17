---
copy: template-climbuk-purchase-order
deliverable: ClimbUK purchase order: Excel template and its LibreOffice copy
build: templates/_build/excel_build.py
files: ClimbUK_Purchase-order.xltx ../../libreoffice/ClimbUK/ClimbUK_Purchase-order.ots
---

# ClimbUK purchase order

<!-- note: One section for each line of words in the workbook, in the order the build writes them: titles, column headings, labels, sample rows and drop-down values. Sheet tab names stay in the build, because formulas refer to them. A drop-down value or a heading that a formula checks (Done, Signed, Live, Revenue) must keep the same words, or the formula stops matching. -->

<!-- note: The drop-down messages and the lists every workbook shares are in templates/office/excel-shared.copy.md. -->

## Form

<!-- @form.eyebrow -->
Purchase order

<!-- @form.sub -->
Quote this number on your invoice.

<!-- @form.number -->
Purchase order number

<!-- @form.dated -->
Order date

<!-- @form.third -->
Required by

<!-- @form.to -->
Supplier

<!-- @form.close -->
Send invoices to [email] quoting the purchase order number. Payment within 14 days of a correct invoice.

<!-- @form.ordered-by -->
Ordered by

<!-- @form.address-line-1 -->
[Address line 1]

<!-- @form.town-postcode -->
[Town, Postcode]

<!-- @form.vat-number -->
VAT number {number}

<!-- @form.company-name -->
[Company name]

<!-- @form.contact-name -->
[Contact name]

<!-- @form.reference -->
Reference

<!-- @form.your-reference -->
[Your reference]

<!-- @form.description -->
Description

<!-- @form.quantity -->
Quantity

<!-- @form.unit-price -->
Unit price

<!-- @form.total -->
Total

<!-- @form.item -->
[Item]

<!-- @form.subtotal -->
Subtotal

<!-- @form.vat-rate -->
VAT rate

<!-- @form.vat -->
VAT

## Print setup

<!-- @print-setup.page-p-of-n -->
Page &P of &N
