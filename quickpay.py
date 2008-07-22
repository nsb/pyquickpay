"""
QuickPay - Interface to the QuickPay gateway
"""
import urllib
import logging
import md5
from xml.dom import minidom

class QuickPayError(Exception):
    pass

class QuickPay(object):
    def __init__(self, merchant, secretkey):
        self.merchant = merchant
        self.secretkey = secretkey
        self.url = 'https://secure.quickpay.dk/transaction.php'

    def _do_post(self, data):
        try:
            url_obj = urllib.urlopen(self.url, urllib.urlencode(data))
            doc = minidom.parse(url_obj)
            elm = doc.documentElement
            msgtype = elm.getAttribute('msgtype')
            pbsstat = elm.getAttribute('pbsstat')
            qpstat = elm.getAttribute('qpstat')
            qpstatmsg = elm.getAttribute('qpstatmsg')
            assert qpstat == '000'
            assert pbsstat == '000'
            if data['msgtype'] == '1100': assert msgtype == '1110'
            elif data['msgtype'] == '1220': assert msgtype == '1230'
        except (IOError, AssertionError), e:
            raise

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

        while len(ordernum) < 4:
            ordernum = '0' + ordernum

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


    def credit(self):
        pass

    def pbsstatus(self):
        pass