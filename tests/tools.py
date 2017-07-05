#This file is part esale module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from decimal import Decimal
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT

__all__ = ['sale_configuration', 'sale_values', 'lines_values', 'party_values',
    'invoice_values', 'shipment_values']

def sale_configuration():
    "Update sale configuration"
    Account = POOL.get('account.account')
    Configuration = POOL.get('sale.configuration')
    Uom = POOL.get('product.uom')
    Category = POOL.get('product.category')
    Template = POOL.get('product.template')
    Product = POOL.get('product.product')
    Location = POOL.get('stock.location')
    PaymentType = POOL.get('account.payment.type')
    PaymentTerm = POOL.get('account.invoice.payment_term')
    PaymentTermLine = POOL.get('account.invoice.payment_term.line')
    PriceList = POOL.get('product.price_list')
    PriceListLine = POOL.get('product.price_list.line')
    Currency = POOL.get('currency.currency')

    unit, = Uom.search([('name', '=', 'Unit')])
    warehouse, = Location.search([('type', '=', 'warehouse')])
    currency, = Currency.search([], limit=1)
    account_expense, = Account.search([('kind', '=', 'expense')])

    # category
    category = Category()
    category.name = 'Category'
    category.account_expense = account_expense
    category.save()

    # products
    ptypes = ['delivery', 'discount', 'surcharge', 'fee']
    for ptype in ptypes:
        ts = Template()
        ts.name = ptype.title()
        ts.type = 'service'
        ts.salable = True
        ts.category = category
        ts.list_price = Decimal('0.0')
        ts.cost_price = Decimal('0.0')
        ts.default_uom = unit
        ts.sale_uom = unit
        ts.account_category = True
        ts.taxes_category = True
        ps = Product()
        ps.code = ptype[:3].upper()
        ts.products = [ps]
        ts.save()

    delivery, discount, surcharge, fee = Product.search([
        ('code', 'in', [ptype[:3].upper() for ptype in ptypes]),
        ])

    # payment type
    paytype = PaymentType()
    paytype.name = 'Bank Transf'
    paytype.code = 'BTRANS'
    paytype.kind = 'receivable'
    paytype.save()

    # payment term
    payterm = PaymentTerm()
    payterm.name = '0 days'
    paytermline = PaymentTermLine()
    paytermline.type = 'remainder'
    payterm.lines = [paytermline]
    payterm.save()

    # price list
    plist = PriceList()
    plist.name = 'Public'
    plistline = PriceListLine()
    plistline.formula = 'unit_price'
    plist.lines = [plistline]
    plist.save()

    # configuration
    configuration = Configuration(1)
    configuration.sale_delivery_product = delivery
    configuration.sale_discount_product = discount
    configuration.sale_surcharge_product = surcharge
    configuration.sale_fee_product = fee
    configuration.sale_uom_product = unit
    configuration.sale_warehouse = warehouse
    configuration.sale_payment_type = paytype
    configuration.sale_payment_term = payterm
    configuration.sale_price_list = plist
    configuration.sale_currency = currency
    configuration.sale_category = category
    configuration.save()

def sale_values(reference):
    vals = {
        'reference_external': reference,
        'carrier': 'carrier',
        'payment': 'cash',
        'currency': 'EUR',
        'comment': 'Example Sale Order',
        'status': 'paid',
        'status_history': 'status history',
        'external_untaxed_amount': Decimal('20.00'),
        'external_tax_amount': Decimal('5.00'),
        'external_total_amount': Decimal('25.00'),
        'external_shipment_amount': Decimal('12.10'),
        'shipping_price': '10.00',
        'shipping_note': 'eSale External',
        'discount': '',
        'discount_description': '',
        'coupon_code': '',
        'coupon_description': '',
        }
    return vals

def lines_values(code):
    vals = {
        'product': code,
        'quantity': '1.0',
        'description': 'Product eSale',
        'unit_price': '10.00',
        'note': '',
        'sequence': 1,
        }
    return vals

def party_values():
    vals = {
        'name': 'Customer',
        'esale_email': 'email@domain.com',
        'vat_code': 'A78109592',
        'vat_country': 'ES',
        }
    return vals

def invoice_values():
    vals = {
        'name': 'Invoice Address',
        'street': 'Durruti',
        'zip': '08000',
        'city': 'Barcelona',
        'subdivision': '',
        'country': 'ES',
        'phone': '0034890',
        'email': 'email@domain.com',
        'fax': '',
        }
    return vals

def shipment_values():
    vals = {
        'name': 'Delivery Address',
        'street': 'Ovidi Montllor',
        'zip': '08000',
        'city': 'Barcelona',
        'subdivision': '',
        'country': 'ES',
        'phone': '0034890',
        'email': 'email@domain.com',
        'fax': '',
        }
    return vals
