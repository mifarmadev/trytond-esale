# This file is part esale module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
import stdnum.eu.vat as vat
import logging

__all__ = ['Party']
__metaclass__ = PoolMeta

logger = logging.getLogger(__name__)
_ESALE_PARTY_EXCLUDE_FIELDS = ['vat_country', 'vat_code']


class Party:
    __name__ = 'party.party'
    esale_email = fields.Char('E-Mail')

    @classmethod
    def view_attributes(cls):
        return super(Party, cls).view_attributes() + [
            ('//page[@id="esale"]', 'states', {
                    'invisible': ~Eval('esale_email'),
                    })]

    @classmethod
    def esale_create_party(self, shop, values):
        '''
        Create Party
        :param shop: obj
        :param values: dict
        return party object
        '''
        pool = Pool()
        Party = pool.get('party.party')
        Identifier = pool.get('party.identifier')
        ContactMechanism = pool.get('party.contact_mechanism')

        vat_code = values.get('vat_code')
        vat_country = values.get('vat_country')

        is_vat = False
        if vat_country and vat_code:
            code = '%s%s' % (vat_country.upper(), vat_code)
            if vat.is_valid(code):
                vat_code = code
                is_vat = True

        #  Search party by:
        #  - VAT country + VAT code
        #  - VAT code
        #  - Party eSale Email
        #  - Party Email
        party = None
        # search by VAT
        if shop.esale_get_party_by_vat and vat_code:
            parties = Party.search([
                ('identifier_code', '=', vat_code),
                ], limit=1)
            if not parties and is_vat:
                parties = Party.search([
                    ('identifier_code', '=', vat_code[2:]),
                    ], limit=1)
            if parties:
                party, = parties
        # search by esale email
        if not party:
            parties = Party.search([
                ('esale_email', '=', values.get('esale_email')),
                ], limit=1)
            if parties:
                party, = parties
        # search by mechanism email
        if not party:
            mechanisms = ContactMechanism.search([
                ('type', '=', 'email'),
                ('value', '=', values.get('esale_email')),
                ], limit=1)
            if mechanisms:
                mechanism, = mechanisms
                party = mechanism.party

        # not found, create
        if not party:
            party = Party()
            for k, v in values.iteritems():
                if k not in _ESALE_PARTY_EXCLUDE_FIELDS:
                    setattr(party, k, v)
            party.addresses = None
            if vat_code:
                identifier = Identifier()
                identifier.code = vat_code
                if is_vat:
                    identifier.type = 'eu_vat'
                party.identifiers = [identifier]
            party.save()

            logger.info('Shop %s. Created party ID %s' % (
                shop.name, party.id))
        return party
