'''
Description:
These python classes create and describe the database tables needed
for our project.
'''


from django.db import models

class User(models.Model):
  # userName: A unique string for each user, used to log in and displayed to
  #      other users
  user_name = models.CharField(max_length=100)

  do_place_list = models.TextField()
  done_place_list = models.TextField()

  friends_list = models.TextField()

class Place(models.Model):
  place_name = models.CharField(max_length=100)
  lat = models.FloatField()
  lng = models.FloatField()
