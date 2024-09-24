# Coffee Shop Full Stack

## Full Stack Nano - IAM Final Project

This project uses Flask and Auth0 to implement identity and access management.
These are the goals for the project

1. Display graphics representing the ratios of ingredients in each drink.
2. Allow public users to view drink names and graphics.
3. Allow the shop baristas to see the recipe information.
4. Allow the shop managers to create new drinks and edit existing drinks.

## Backend
```
$ FLASK_APP=api.py FLASK_DEBUG=True flask run
```
  
## Frontend
```
$ export NODE_OPTIONS=--openssl-legacy-provider
```

```
$ ionic serve -c --ssl --external
```