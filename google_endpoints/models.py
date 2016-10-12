"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    target = ndb.GenericProperty(repeated=True) #1 to 52 random sequence
    bingo= ndb.GenericProperty(repeated=True) #array of tuple (indexA, indexB) that are paired
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    
    #get_game_history api
    indA_history= ndb.GenericProperty(repeated=True) 
    indB_history= ndb.GenericProperty(repeated=True) 
    result = ndb.GenericProperty(repeated=True) 
    status = ndb.StringProperty(default='active') 
    
    @classmethod
    def new_game(cls, user, attempts):
        """Creates and returns a new game"""

        game = Game(user=user,
                    target=random.sample(range(0,52),52), #digitalize the cards
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    game_over=False)
        game.put()
        return game
    
    def indexCard(self, ind):
        '''
        translate the number into rank & color of the card
        for example 1 = 1 diamond, 2 = 1 club, 3 = 1 heart, 4 = 1 spade
        5 = 2 diamond, 6 = 2 club
        for simplicity we use rank 11 as Jack, rank 12 as Queen, rank 13 as King
        '''
        num = self.target[ind]
        shape = ['diamond', 'club', 'heart', 'spade']
        key = (num / 4)
        rank = key +1
        cshape = shape[(num - key*4)]

        return (rank, cshape)
        
    def bingoPair(self, cardA, cardB):
        if cardA[0] == cardB[0]: #check for rank
          red = ['diamond', 'heart']
          black = ['club', 'spade']
          if (cardA[1] in red and cardB[1] in red) or \
            (cardA[1] in black and cardB[1] in black):
            return True
        else:
          return False
        
    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      matches=len(self.bingo)/2)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    matches = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), matches=self.matches)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)

class GameForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)    

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    attempts = messages.IntegerField(2, default=5)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    indexA = messages.IntegerField(1, required=True)
    indexB = messages.IntegerField(2, required=True)

    

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    matches = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)

class RankForm(messages.Message):
    """RankForm for outbound Rank information"""
    user_name = messages.StringField(1, required=True)
    performance = messages.FloatField(2, required=True)

class RankForms(messages.Message):
    """Return multiple RankForms"""
    items = messages.MessageField(RankForm, 1, repeated=True)

class HistoryForm(messages.Message):
    """HistoryForm for outbound History information"""
    guess = messages.StringField(1, required=True)
    result = messages.StringField(2, required=True)

class HistoryForms(messages.Message):
    """Return multiple HistoryForms"""
    items = messages.MessageField(HistoryForm, 1, repeated=True)    
class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
