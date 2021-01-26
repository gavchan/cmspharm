import pytz
from django.utils import timezone

# make sure you add `TimezoneMiddleware` appropriately in settings.py
class TimezoneMiddleware(object):
    """
    Middleware to properly handle the users timezone
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"TZ request:{request}")
        tzname = 'UTC'
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        # otherwise deactivate and the default time zone will be used anyway
        else:
            print("No tzname")
            timezone.deactivate()

        response = self.get_response(request)
        return response
