from django.conf.urls import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # view sets, create a set, and delete a set
    (r'^.*$','flashcards.views.home'),
    (r'^get_sna/$', 'flashcards.views.get_sna'),

)
