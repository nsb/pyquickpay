from quickpay import QuickPay
import unittest
import string
import random

try:
    from quickpay_settings import *
except ImportError:
    import sys
    sys.stderr.write('Unable to read quickpay_settings.py\n')
    sys.exit(1)


class TestQuickPay(unittest.TestCase):

    def _ordernum(self):
        return ''.join([random.choice(string.digits) for x in xrange(20)])

    def setUp(self):
        self.merchant = MERCHANT_ID
        self.secret_key = SECRET_KEY
        self.cardnumber = CARD_NUMBER
        self.amount = 100
        self.currency = 'DKK'
        self.expirationdate = EXPIRATION_DATE
        self.cvd = CVD
        self.qp = QuickPay(merchant=self.merchant, secretkey=self.secret_key, pretend=True)

    def testAuthorizeCapture(self):
        # authorize
        transaction = self.qp.authorize(cardnumber=self.cardnumber,
                                        amount=self.amount,
                                        ordernum=self._ordernum(),
                                        currency=self.currency,
                                        expirationdate=self.expirationdate,
                                        cvd=self.cvd)

        # capture
        self.qp.capture(transaction, self.amount * 100)


    def testSubscription(self):
        # preauth
        preauth_ordernum = self._ordernum()
        preauth_transaction = self.qp.authorize(cardnumber=self.cardnumber,
                                                amount=self.amount,
                                                ordernum=preauth_ordernum,
                                                currency=self.currency,
                                                expirationdate=self.expirationdate,
                                                cvd=self.cvd,
                                                authtype='preauth',
                                                reference=preauth_ordernum)

        # recurring
        recurring_transaction = self.qp.authorize(amount=self.amount,
                                                  ordernum=self._ordernum(),
                                                  currency=self.currency,
                                                  authtype='recurring',
                                                  transaction=preauth_transaction)

        # capture subscription
        self.qp.capture(recurring_transaction, self.amount)

        # cancel subscription
        self.qp.reversal(preauth_transaction)


if __name__ == '__main__':
    unittest.main()