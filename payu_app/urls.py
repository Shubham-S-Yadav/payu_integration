"""
This file is used as routes for the service app API's.
"""
from django.conf.urls import url
from .views import (SuccessView,
                    GenerateHashKeyView
                    )

urlpatterns = [
    url('generateHashKey', GenerateHashKeyView.as_view(), name="generate-hash"),
    url('success', SuccessView.as_view(), name="success"),
]
