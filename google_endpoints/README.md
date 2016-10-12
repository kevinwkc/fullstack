#Full Stack Nanodegree Project 4 Refresh

## Set-Up Instructions:

http://game-api-146120.appspot.com

OR

1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
Concentration: https://en.wikipedia.org/wiki/Concentration_(game)
a standard deck of 52 cards, which are normally laid face down in 1 rows of 52 cards.

Chooses two cards and turns them face up. If they are of the same rank and color (e.g. six of hearts and six of diamonds, queen of clubs and queen of spades, or both jokers, if used) then that player wins the pair and plays again. If they are not of the same rank and color, they are turned face down again and play passes to the player on the left. 

you win if you got MORE OR EQUAL TO (attempt/2) pair match in 'attempts'

0-based Index, so the first card is at slot 0, second card is at slot 1;

2 'Slot'(indexA, indexB) are sent to the `make_move` endpoint which will reply
with either: 'Bingo with information about the 2 card', 'Try Again with information about the 2 card', 'you win', or 'game over' (if the maximum
number of attempts is reached).

This is one-player Concentration game. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - README.md: desciption about each api, deployment instruction, data model, messages forms
 - Design.md: reflection on learning scalable arch.
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.


##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name,  attempts
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Also adds a task to a task queue to update the average moves remaining for active games.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, indexA, indexB
    - Returns: GameForm with new game state.
    - Description: Accepts 2 slot - indexA, indexB and returns the updated state of the game.
    It will provide information about the 2 card you picked ie) 2 diamond, 5 spade
    Tell you whether it a matches or try again
    "Illegal" moves are handled gracefully by the API - if player try to guess the same matched second times.
    You will have to guess until you reach 'attempts' of trys
    If this causes a game to end, a corresponding Score entity will be created.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_active_game_count**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts remaining for all games
    from a previously cached memcache key.

    - **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name, email (optional)
    - Returns: Message GameForms of GameForm for the user
    - Description: 
    This returns all of a User's active games.

- **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: VoidMessage if successful delete
    - Description: 
    This endpoint allows users to cancel a game in progress. 

- **get_high_scores**
    - Path: 'scores/lead'
    - Method: GET
    - Parameters: number_of_results
    - Returns: Message ScoreForms of ScoreForm for all games
    - Description: 
    generate a list of high scores in descending order, a leader-board!
    Accept an optional parameter number_of_results that limits the number of results returned.   

- **get_user_rankings**
    - Path: 'user/rank'
    - Method: GET
    - Parameters: n/a
    - Returns: Message RankForms of RankForm for all user
    - Description: 
    returns all players ranked by performance.
    performance metric = sum(matches/attempt) / count(game) 
    The results should include each Player's name and the 'performance' indicator (eg. win/loss ratio).

- **get_game_history**
    - Path: 'game/history/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: Message HistoryForms of HistoryForm for that game
    - Description: 
    Your API Users may want to be able to see a 'history' of moves for each game.
    like this:
    {
 "items": [
  {
   "guess": "(15L, 20L)",
   "result": "Try Again - IndexA: (6L, 'heart') & Index B: (3L, 'heart')"
  },
  {
   "guess": "(26L, 48L)",
   "result": "Bingo! pair: (1L, 'heart') & (1L, 'diamond')"
  },
  {
   "guess": "(50L, 45L)",
   "result": "Bingo! pair: (1L, 'club') & (1L, 'spade')"
  },
  {
   "guess": "(4L, 34L)",
   "result": "Bingo! pair: (2L, 'diamond') & (2L, 'heart')"
  }
 ]
}
    
##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
 - **RankForm**
    - Representation of performance for user (user_name, performance)
 - **RankForms**
    - Multiple RankForm container.
 - **HistoryForm**
    - Representation of game steps for the game (guess, result)
 - **HistoryForms**
    - Multiple HistoryForm container.    