# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

from __future__ import division
import logging
import endpoints
from protorpc import remote, messages
from protorpc import message_types
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, GameForms, RankForms, RankForm, HistoryForms, HistoryForm
from utils import get_by_urlsafe


NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
HIGH_SCORES_REQUEST = endpoints.ResourceContainer(
    number_of_results=messages.IntegerField(1),)
MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'


@endpoints.api(name='concentration', version='v1')
class ConcentrationApi(remote.Service):

    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))

    @endpoints.method(
        response_message=RankForms,
        path='user/rank',
        name='get_user_rankings',
        http_method='GET')
    def get_user_rankings(self, request):
        """
        returns all players ranked by performance
        metric = sum(matches/attempt) / count(game)
        """

        prank = {}
        users = User.query().fetch()
        for u in users:
            gamesByUser = Game.query(Game.user == u.key)
            gamesByUser = gamesByUser.filter(Game.status != 'active').fetch()
            if len(gamesByUser) > 0:
                perf = sum(
                    [(len(g.bingo)/2)/g.attempts_allowed for g in gamesByUser])/len(gamesByUser)
                prank[u.name] = perf

        sorted_prank = sorted(prank.items(), key=lambda x: -x[1])

        return RankForms(items=[RankForm(user_name=r[0], performance=r[1]) for r in sorted_prank])

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')

        game = Game.new_game(user.key, request.attempts)

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Concentration!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=HistoryForms,
                      path='game/history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """ see a 'history' of moves for each game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game:
            return HistoryForms(items=[HistoryForm(guess=str((a, b)), result=r)
              for a, b, r in zip(game.indA_history, game.indB_history, game.result)])
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=message_types.VoidMessage,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.game_over is False:
                game.key.delete()
                return message_types.VoidMessage()
            else:
                raise endpoints.BadRequestException(
                    'Users are not permitted to remove completed games!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')

        if request.indexA == request.indexB or \
                (request.indexA < 0 or request.indexA > 51) or \
                (request.indexB < 0 or request.indexB > 51):
            raise endpoints.BadRequestException(
                'Index should be difference in [0,51] range.')

        game.attempts_remaining -= 1

        cardA = game.indexCard(request.indexA)
        cardB = game.indexCard(request.indexB)

        if game.bingoPair(cardA, cardB):
            # check for illegal move
            if request.indexA not in game.bingo:
                game.bingo = game.bingo+[request.indexA, request.indexB]
                msg = 'Bingo! pair: ' + str(cardA) + " & " + str(cardB)
            else:
                raise endpoints.BadRequestException(
                    'Illegal moves - pair already bingo before.')
        else:
            msg = 'Try Again - IndexA: ' + str(cardA) + \
                " & Index B: " + str(cardB)

        # save history for get_game_history
        game.indA_history = game.indA_history + [request.indexA]
        game.indB_history = game.indB_history + [request.indexB]
        game.result = game.result + [msg]

        msg += "Game Board: " + str([(str(a) + ':' + str(game.indexCard(a)) +
              " & " + str(b) + ':' + str(game.indexCard(b)))
              for a, b in zip(game.indA_history, game.indB_history)])

        if game.attempts_remaining < 1:
            if (len(game.bingo)/2) >= (game.attempts_allowed/2):
                # same the status of game
                game.status = 'won'
                game.end_game(True)
                return game.to_form(msg + ' You Win!')
            else:
                game.status = 'lost'
                game.end_game(False)
                return game.to_form(msg + ' Game over!')
        else:
            game.status = 'active'
            game.put()
            return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=HIGH_SCORES_REQUEST,
                      response_message=ScoreForms,
                      path='scores/lead',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """generate a list of high scores in descending order"""

        scores = Score.query(
        ).order(-Score.matches).fetch(request.number_of_results)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """This returns all of a User's active games."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')

        games = Game.query(Game.user == user.key)
        games = games.filter(Game.status == 'active').fetch()
        return GameForms(items=[game.to_form('') for game in games])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _game_incomplete(user_key):
        games = Game.query(Game.user == user_key)
        for g in games:
            if g.game_over is False:
                return True

        return False

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                            for game in games])
            average = float(total_attempts_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([ConcentrationApi])
