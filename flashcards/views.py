'''
General Description:
Entering a certain url (into a browser) calls a view function
based on the mappings described in the urls.py file.
These functions take a request and url
digits as parameters. They interface with
models and templates.
'''

from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponseServerError, HttpResponse
from django.shortcuts import render
from django.contrib.auth import logout
from django.core.servers.basehttp import FileWrapper
import os, tempfile, zipfile

HOME = os.getcwd()
MAX_SIZE_SETS = 100

'''returns sna html'''
def sna(request):
  return render(request, 'fc/SNA.html')

def home(request):
  return render(request, 'fc/home.html')


''' return sna.py project '''
def get_sna(request):
  response = getFileResponse('sna.py')
  return response

''' returns AI meta-tic-tac-toe '''
def meta(request):
  return render(request, 'fc/Meta_Tic-Tac-Toe.html')

''' returns AI meta-tic-tac-toe '''
def get_meta(request):
  response = getFileResponse('meta.py')
  return response

''' returns learning.py '''
def get_learning(request):
  response = getFileResponse('learning.py')
  return response

''' return a file attachment for given filename '''
def getFileResponse(filename):
  fullFN = HOME + '/media/' + filename
  trio = open(fullFN, 'r')
  list = trio.readlines()
  result = reduce( (lambda x, y: x+y), list)
  response = HttpResponse(result)
  response['Content-Disposition'] = 'attachment; filename = ' + fullFN
  return response

''' return file response '''
def get_trio(request):
  print "WAS called trololol"
  response = getFileResponse('trio.py')
  print "was reached i dunno"
  return response

''' show printable resume '''
def printable_resume(request):
  return render(request, 'fc/printable_resume.html')

''' show my resume '''
def resume(request):
  get_trio = '/get_trio/'
  return render(request, 'fc/Resume.html', {'get_trio': get_trio,})

''' lists card in current set '''
def list_card(request, setID):
  cardList = cardTable.objects.filter(setID = setID).order_by('cardID')[0:MAX_SIZE_SETS]
  assert len(cardList) == len(cardTable.objects.filter(setID=setID)) #defensive programming
  url_create = "/create/" + str(setID) + "/"
  return render(request, 'fc/list.html', {'card_list': cardList, 'url_create': url_create,})

''' shows details of a card '''
def show_card(request, setID, cardID):
  list_url = "/set/" + setID + "/"
  return render(request, 'fc/fc_detail.html', {'object': cardTable.objects.filter(setID=setID).get(cardID=cardID), 'list_url': list_url,})

def delete_card(request, setID, cardID):
  deleteMe = cardTable.objects.filter(setID=setID).get(cardID = cardID)
  deleteMe.delete()
  return HttpResponsePermanentRedirect('/set/'+str(setID)+'/')

''' Creates a new card '''
def create_card(request, setID):
  if request.method == "POST":
    post = request.POST.copy()
    if post.has_key('front') and post.has_key('back'):
      order = len(cardTable.objects.filter(setID = setID)) #later must check for int
      if cardTable.objects.filter(cardID=order).filter(setID=setID).count() == 0:
        if len(cardTable.objects.all()) <= MAX_SIZE_SETS:
          front = post['front']
          back = post['back']
          new_flashcard = cardTable.objects.create(cardID=order, setID=setID, front=front, back=back)
          return HttpResponsePermanentRedirect('/set/%s'% setID)
        else: error_msg = u"Maximum size of set reached. Please create a new set to add more flashcards."
      else: error_msg = u"Please enter an integer value."
    else: error_msg = u"Insufficient POST data (enter in forms)"
  else: error_msg = u"No POST data sent."
  return HttpResponseServerError(error_msg)

''' allows card to be modified '''
def update_card(request, setID, cardID):
  if request.method == "POST":
    post = request.POST.copy()
    flashcard = cardTable.objects.filter(setID=setID).get(cardID=cardID)
    if post.has_key('front'):
      flashcard.front = post['front']
    if post.has_key('back'):
      flashcard.back = post['back']
    flashcard.save()
    return HttpResponseRedirect(flashcard.get_absolute_url())
  else: error_msg = u"No POST data sent."
  return HttpResponseServerError(error_msg)

''' lists the contents of a set '''
def list_materials(request):
  setList = userSetTable.objects.order_by('setID')[0:MAX_SIZE_SETS]
  assert len(setList) == len(userSetTable.objects.all())
  print "length of setList", len(setList), "length of all", len(userSetTable.objects.all())
  trio_url = '/get_trio/'
  return render(request, 'fc/user.html', {'set_list': setList, 'trio_url': trio_url,})

''' deletes the current set '''
def delete_set(request, setID):
  deleteMe = userSetTable.objects.get(setID = setID)
  deleteCards = cardTable.objects.filter(setID = setID)
  for delCard in deleteCards:
    delCard.delete()
  deleteMe.delete()
  return HttpResponsePermanentRedirect('/user/')

''' creates a new set '''
def create_set(request):
  if request.method == "POST":
    post = request.POST.copy()
    if (post.has_key('setName') and len(post['setName']) > 0 and
          len(userSetTable.objects.filter(setName = post['setName'])) == 0):
      if len(userSetTable.objects.all()) < MAX_SIZE_SETS:
        order = len(userSetTable.objects.all())
        setName = post['setName']
        new_set = userSetTable.objects.create(setID=order, setName=setName)
        return HttpResponsePermanentRedirect('/user/')
      else: error_msg = u"Maximum size of sets reached. Please delete some of you sets."
    else: error_msg = u"Enter unique and valid set name"
  else: error_msg = u"No POST data sent."
  return HttpResponseServerError(error_msg)

''' user functionality not implemented yet '''
def log_out(request):
  logout(request)
  return HttpResponseServerError("User accounts not implemented yet.")

'''
sets all cards as unreviewed when we start a review session
(this is a wrapper function)
'''
def start_review(request, setID, cardID, gotRight):
  allCards = cardTable.objects.filter(setID = setID)
  for card in allCards:
    # Now that we are finish with set, reset right values
    card.right = False
    card.save()
  return get_next_card(request, setID, cardID, gotRight)

'''
Handles the result of calling next card
Calls the review function
'''
def get_next_card(request, setID, cardID, gotRight):
  setID = int(setID)
  cardID = int(cardID)
  if eval(gotRight):
    done_flashcard = cardTable.objects.get(setID=setID, cardID=cardID)
    done_flashcard.right = True
    done_flashcard.save()
  cardsLeft = cardTable.objects.filter(setID=setID, right=False)
  if(cardsLeft):
    cardsLeft = cardsLeft.order_by('cardID')
  if len(cardsLeft) == 0:
    return review(request, setID, -1)
  elif len(cardsLeft) == 1:
    return review(request, setID, cardsLeft[0].cardID)
  elif len(cardsLeft) > 1:
    print "cardID", cardID
    cardsAfter = cardsLeft[cardID+1: MAX_SIZE_SETS]
    if len(cardsAfter) > 0:
      # try to find a card with a larger cardID
      print "cardAfter", cardsAfter
      return review(request, setID, cardsAfter[0].cardID)
    else:
      # pick card with smallest cardID 
      print "CardsLeft", cardsLeft
      return review(request, setID, cardsLeft[0].cardID)

''' returns render request '''
def review(request, setID, cardID):
  if cardID == -1:
    allCards = cardTable.objects.filter(setID=setID)
    for card in allCards:
      # Now that we are finish with set, reset 'right' values
      card.right = False
      card.save()
    return render(request, 'fc/congrats.html')
  nextCard = cardTable.objects.get(setID=setID, cardID = cardID, right=False)
  return render(request, 'fc/review.html', {'flashcard': nextCard,})
