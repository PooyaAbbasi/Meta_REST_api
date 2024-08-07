from rest_framework.throttling import UserRateThrottle


class TenUserRateThrottle(UserRateThrottle):
    scope = 'ten'
