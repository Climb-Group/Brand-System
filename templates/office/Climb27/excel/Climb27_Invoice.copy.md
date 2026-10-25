---
copy: template-climb27-invoice
deliverable: Climb27 invoice: Excel template and its LibreOffice copy
build: templates/_build/excel_build.py
files: Climb27_Invoice.xltx ../../libreoffice/Climb27/Climb27_Invoice.ots
---

# Climb27 invoice

<!-- note: One section for each line of words in the workbook, in the order the build writes them: titles, column headings, labels, sample rows and drop-down values. Sheet tab names stay in the build, because formulas refer to them. A drop-down value or a heading that a formula checks (Done, Signed, Live, Revenue) must keep the same words, or the formula stops matching. -->

<!-- note: The drop-down messages and the lists every workbook shares are in templates/office/excel-shared.copy.md. -->

## Form

<!-- @form.eyebrow -->
Invoice

<!-- @form.sub -->
Payable within 14 days of the invoice date.

<!-- @form.number -->
Invoice number

<!-- @form.dated -->
Invoice date

<!-- @form.third -->
Due date

<!-- @form.to -->
Bill to

<!-- @form.close -->
Pay by bank transfer to [Account name], sort code [00-00-00], account [00000000], quoting the invoice number. Questions to [email].

<!-- @form.from -->
From

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
