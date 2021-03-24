from django.http import HttpResponse


class StripeWH_Handler:
    """"Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
      """
      Handle a generic webhook event
      """
      return HttpResponse(
          content=f'Webhook received from stripe: {event["type"]}',
          status=200)