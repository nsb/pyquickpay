"""
QuickPay - Interface to QuickPay payment gateway, http://www.quickpay.dk
Author: Niels Sandholt Busch, Spacergif Software 2008
"""
import urllib
import logging
import md5
from xml.dom import minidom
import string
import random

class QuickPayError(Exception):
    "Indicates the operation failed"

class QuickPay(object):
    """
    Implements Quickpay payment gateway. Use pretend = True for testing
    """
    def __init__(self, merchant, secretkey, pretend=False):
        self.merchant = merchant
        self.secretkey = secretkey
        self.pretend = pretend
        self.url = 'https://secure.quickpay.dk/transaction.php'

    def _do_post(self, data):
        msgtypes = {'1100':'1110', '1220':'1230', '1420':'1430'}
        try:
            if self.pretend:
                reply = '<?xml version="1.0" encoding="ISO-8859-1"?> \
                         <values msgtype="%s" pbsstat="000" qpstat="000" qpstatmsg="OK" transaction="%s" />' \
                         % (msgtypes[data['msgtype']], ''.join([random.choice(string.digits) for x in xrange(7)]))
                doc = minidom.parseString(reply)
            else:
                url_obj = urllib.urlopen(self.url, urllib.urlencode(data))
                doc = minidom.parse(url_obj)
            elm = doc.documentElement
            msgtype = elm.getAttribute('msgtype')
            pbsstat = elm.getAttribute('pbsstat')
            qpstat = elm.getAttribute('qpstat')
            qpstatmsg = elm.getAttribute('qpstatmsg')
            assert qpstat == pbsstat == '000'
            assert msgtype == msgtypes[data['msgtype']]
        except IOError, e:
                raise QuickPayError, e
        except AssertionError, e:
            raise QuickPayError, qpstatmsg

        return elm


    def authorize(self,
                  cardnumber=None,
                  amount=None,
                  ordernum=None,
                  currency=None,
                  expirationdate=None,
                  cvd=None,
                  authtype=None,
                  reference=None,
                  transaction=None):
        """
        Authorize
        """
        msgtype = '1100'
        posc = 'K00540K00130' if (authtype or '') == 'recurring' else 'K00500K00130'
        data = {}

        if authtype == 'recurring':
            cardnumber = ''
            expirationdate = ''
            cvd = ''
            data.update({'authtype':authtype, 'transaction':transaction})

        if authtype == 'preauth':
            amount = 100
            data.update({'authtype':authtype, 'reference':reference})

        ordernum = ''.join(['0' for i in range(4-len(ordernum))]) + ordernum

        data.update({'msgtype':msgtype,
                     'cardnumber':cardnumber,
                     'amount':amount,
                     'expirationdate':expirationdate,
                     'posc':posc,
                     'ordernum':ordernum,
                     'currency':currency,
                     'cvd':cvd,
                     'merchant':self.merchant})

        md_input = ''.join((msgtype,
                            cardnumber or '',
                            str(amount),
                            expirationdate or '',
                            posc,
                            str(ordernum),
                            currency,
                            str(cvd or ''),
                            self.merchant,
                            authtype or '',
                            reference or '',
                            transaction or '',
                            self.secretkey))
        md5checkV2 = md5.new(md_input).hexdigest().upper()
        data['md5checkV2'] = md5checkV2

        elm = self._do_post(data)
        transaction = elm.getAttribute('transaction')
        return transaction


    def capture(self, transaction, amount):
        """
        Capture
        """
        msgtype = '1220'
        md_input = ''.join((msgtype,
                           str(amount),
                           self.merchant,
                           transaction,
                           self.secretkey))
        md5check = md5.new(md_input).hexdigest().upper()

        data = {'msgtype':msgtype,
                'amount':amount,
                'merchant':self.merchant,
                'transaction':transaction,
                'md5check':md5check}

        elm = self._do_post(data)


    def reversal(self, transaction):
        """
        Reversal
        """
        msgtype = '1420'

        md_input = ''.join((msgtype,
                            self.merchant,
                            transaction,
                            self.secretkey))
        md5check = md5.new(md_input).hexdigest().upper()

        data = {'msgtype':msgtype,
                'merchant':self.merchant,
                'transaction':transaction,
                'md5check':md5check}

        self._do_post(data)


    def credit(self):
        pass

    def status(self):
        pass

    def pbsstatus(self):
        pass