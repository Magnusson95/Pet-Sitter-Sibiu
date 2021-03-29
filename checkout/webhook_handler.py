from django.http import HttpResponse

from .models import Order, OrderLineItem
from products.models import Service

import json
import time


class StripeWH_Handler:
    """"Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic webhook event
        """
        return HttpResponse(
            content=f'Generic webhook received from stripe: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook event
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        total = round(intent.data.charges[0].amount / 100, 2)

        #clean data in shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=shipping_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.country,
                    postcode__iexact=shipping_details.pstal_code,
                    town_or_city__iexact=shipping_details.city,
                    street_address1__iexact=shipping_details.line1,
                    street_address2__iexact=shipping_details.line2,
                    county__iexact=shipping_details.state,
                    total=total,
                    original_bag=bag,
                    stripe_pid=pid
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            return HttpResponse(
                  content=f'Webhook received from stripe: {event["type"]} |x Syccess: Verified order already in database',
                  status=200)
        else:
            order = None
            try:
                order = order.objects.create(
                    full_name=shipping_details.name,
                    email=shipping_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.country,
                    postcode=shipping_details.pstal_code,
                    town_or_city=shipping_details.city,
                    street_address1=shipping_details.line1,
                    street_address2=shipping_details.line2,
                    county=shipping_details.state,
                    original_bag=bag,
                    stripe_pid=pid
                )
                for item_id, item_data in json.loads(bag).items():
                    service = Service.objects.get(Service, id=item_id)
                    for animal, quantity in item_data['items_by_animal'].items():
                        order_line_item = OrderLineItem(
                            order=order,
                            service=service,
                            quantity=quantity,
                            animal=animal,
                        )
                        order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received from stripe: {event["type"]} | Error {e}',
                    status = 500)
        return HttpResponse(
            content=f'Webhook received from stripe: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle a failed payment_intent webhook event
        """
        return HttpResponse(
            content=f'Webhook received from stripe: {event["type"]}',
            status=200)
