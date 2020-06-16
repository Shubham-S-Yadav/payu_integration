from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from payu.models import Transaction
from hashlib import sha512
import hashlib
from django.conf import settings
from payu_demo_integration.settings import PAYU_MERCHANT_KEY, PAYU_MERCHANT_SALT


class GenerateHashKeyView(GenericAPIView):
    """
    Class for creating API view for Payment gateway homepage.
    """
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwags):
        """
        Function for creating a charge.
        """
        key = PAYU_MERCHANT_KEY
        txnid = str(request.data.get('txnid'))
        amount = str(request.data.get('amount'))
        productinfo = str(request.data.get('productinfo'))
        firstname = str(request.data.get('firstname'))
        email = str(request.data.get('email'))
        salt = PAYU_MERCHANT_SALT

        output_data = {
            'key': key,
            'salt': salt,
            'txnid': txnid,
            'amount': amount,
            'productinfo': productinfo,
            'firstname': firstname,
            'email': email,
        }

        keys = ('txnid', 'amount', 'productinfo', 'firstname', 'email',
                'udf1', 'udf2', 'udf3', 'udf4', 'udf5', 'udf6', 'udf7', 'udf8',
                'udf9', 'udf10')

        def generate_hash(input_data, *args, **kwargs):
            hash_value = str(getattr(settings, 'PAYU_MERCHANT_KEY', None))

            for k in keys:
                if input_data.get(k) is None:
                    hash_value += '|' + str('')
                else:
                    hash_value += '|' + str(input_data.get(k))

            hash_value += '|' + str(getattr(settings, 'PAYU_MERCHANT_SALT', None))
            hash_value = sha512(hash_value.encode()).hexdigest().lower()
            Transaction.objects.create(
                transaction_id=input_data.get('txnid'), amount=input_data.get('amount'))
            return hash_value

        get_generated_hash = generate_hash(request.data)

        output_data['hash_key'] = get_generated_hash

        return Response(output_data)


class SuccessView(GenericAPIView):

    def post(self, request):
        status = request.data["status"]
        firstname = request.data["firstname"]
        amount = request.data["amount"]
        txnid = request.data["txnid"]
        posted_hash = request.data["hash"]
        key = request.data["key"]
        productinfo = request.data["productinfo"]
        email = request.data["email"]
        salt = PAYU_MERCHANT_SALT

        try:
            additional_charges = request.data["additionalCharges"]
            ret_hash_seq = additional_charges + '|' + salt + '|' + status + '|||||||||||' + email + '|' + firstname +\
                           '|' + productinfo + '|' + amount + '|' + txnid + '|' + key
        except Exception:
            ret_hash_seq = salt + '|' + status + '|||||||||||' + email + '|' + firstname + '|' + productinfo + '|'\
                         + amount + '|' + txnid + '|' + key

        resonse_hash = hashlib.sha512(ret_hash_seq.encode()).hexdigest().lower()

        if resonse_hash == posted_hash:
            transaction = Transaction.objects.get(transaction_id=txnid)
            transaction.payment_gateway_type = request.data.get('PG_TYPE')
            transaction.transaction_date_time = request.data.get('addedon')
            transaction.mode = request.data.get('mode')
            transaction.status = status
            transaction.amount = amount
            transaction.mihpayid = request.data.get('mihpayid')
            transaction.bankcode = request.data.get('bankcode')
            transaction.bank_ref_num = request.data.get('bank_ref_num')
            transaction.discount = request.data.get('discount')
            transaction.additional_charges = request.data.get('additionalCharges', 0)
            transaction.txn_status_on_payu = request.data.get('unmappedstatus')
            transaction.hash_status = "Success" if resonse_hash == request.data.get('hash') else "Failed"
            transaction.save()
            message = ["Thank You. Your order status is " + status,
                       "Your Transaction ID for this transaction is " + txnid,
                       "We have received a payment of Rs. " + amount,
                       "Your order will soon be shipped."]
        else:
            message = ["Invalid Transaction. Please try again."]
        output_data = {
            "txnid": txnid,
            "status": status,
            "amount": amount
        }
        return Response(output_data, message)
