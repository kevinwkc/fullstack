
What additional properties did you add to your models and why?
----------------------------------------------------------
GenericProperty, I was try to add a list into it.
It cannot add a list, so I add 2 GenericProperty to save the history for pair

What were some of the trade-offs or struggles you faced when implementing the new game logic?
---------------------------------------------------------------------------------------------------
adding 2 fields - GenericProperty field, concern me about adding too many field in the model.
but then I think during works, I always see 20+ field in a model, so I think this is ok

Understand the purpose of http methods/verbs.
---------------------------------------------------
some best practice I research
GET - read 
POST - should create return path GET to new entity 
DELETE - Delete 
PUT - Update if exist, otw save it; return updated object

request should authentication, secure with authentication
apply version for you api
ok: 200; success: 201; error: 500; bad:400

Understand the separation of views/endpoints and internal models and logic.
------------------------------------------------------------------------------------
endpoints enable separation of front-end and back-end.
help focusing just the business logic.
we can also implement different VIEW for the same data to fit client needs.

Understand why task queues or out-of-sequence running of code is important.
-----------------------------------------------------------------------------
task queues is very useful for time consuming task
out-of-sequence is very useful for independent task

Understand status codes? This might be irrelevant for endpoints thanks to
intuitive endpoints exceptions.
------------------------------------------------------------------------------
compare to http method, endpoints just raise exception.
provide the right message and more relevant message to end user
