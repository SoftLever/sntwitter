## Initial Setup

    python manage.py migrate

    python manage.py createsuperuser


### Admin API Key

    curl -X POST http://example.com/auth/login/ --data '{"username": "admin@example.com" ,"password":"password"}' --header "Content-Type: application/json"


## API Documentation

### Create a new user (Create)

Required Permissions: Admin

    curl -X POST http://example.com/auth/users/ --header "Content-Type: application/json" --header "Authorization: Token admin_token" --data '{"username": "customer@example.com" , "first_name": "Tony", "last_name": "Stark", "company_name":"Stark Industries", "password": "password"}'


### List Users (List)

Required Permissions: Admin

    curl http://example.com/auth/users/ --header "Authorization: Token admin_token"


### Log user in (Generate Token)

    curl -X POST http://example.com/auth/login/ --data '{"username": "customer@example.com" ,"password":"password"}' --header "Content-Type: application/json"


The generated token will expire in 30 days.


### Get a single user (Retrieve)

Required Permissions: User or Admin

    curl http://example.com/auth/users/user_id/ --header "Authorization: Token user_token"


### Update User Details Partially (Partial Update)

Required Permissions: User or Admin

    curl -X PATCH http://example.com/auth/users/user_id/ --header "Content-Type: application/json" --header "Authorization: Token user_token" --data '{"last_name": "Jarvis"}'


### Update all user details (Update)

Required Auth: User or Admin

    curl -X PUT http://example.com/auth/users/user_id/ --header "Content-Type: application/json" --header "Authorization: Token user_token" --data '{"first_name": "Pepper", "last_name": "Pots", "username": "customer@example.com", "company_name": "The Stark Company"}'


### Log user out (Revoke token)

    curl -X POST http://example.com/auth/logout/ --header "Content-Type: application/json" --header "Authorization: Token user_token"


### Log out of all sessions (Revoke all tokens)

    curl -X POST http://example.com/auth/logout-all/ --header "Content-Type: application/json" --header "Authorization: Token user_token"


### Set a password for the user -> Useful for reset functionality

Required Permissions: User or Admin

    curl -X PATCH http://example.com/auth/users/user_id/set-password/ --header "Content-Type: application/json" --header "Authorization: Token user_token" --data '{"password": "password"}'


### Delete a user

Required Permissions: Admin

    curl -X DELETE http://example.com/auth/users/user_id/ --header "Content-Type: application/json" --header "Authorization: Token user_token"


## Other endpoints

This section documents endpoints that will be used by Servicenow instances and Twitter. The only configuration needed on a servicenow instance is importing the required update set. The APIKey table also needs to have at least one API token, generated from the `/auth/login/` endpoint.


### Send a servicenow case event
    
    curl -X POST http://example.com/api/events/ --header "Content-Type: application/json" --header "Authorization: Token user_token"

CURL is purely for illustrative purposes. These API call will actually run from a Servicenow instance.

### Receive events from Twitter

    https://example.com/api/activity/

This endpoint receives account activity events from Twitter, processes messages if the activity is either a direct message or mention, then sends the results to the relevant Servicenow instance.
