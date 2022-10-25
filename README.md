# FUNCTIONALITY OVERVIEW

The following flowchart shows how the program works at a basic level

![Flowchart](/docs/servicenow_twitter_flowchart.jpeg "Flowchart")


# INITIAL SETUP

    docker-compose exec web python manage.py migrate

    docker-compose exec web python manage.py createsuperuser

    docker-compose exec web python manage.py webhooks register --url https://twittnow.softlever.com/twitter-activity


## Admin API Key

    curl -X POST https://twittnow.softlever.com/auth/login/ --data '{"username": "admin@example.com" ,"password":"password"}' --header "Content-Type: application/json"


# API Documentation

## Create a new user (Create)

Required Permissions: Admin

    curl -X POST https://twittnow.softlever.com/auth/users/ --header "Content-Type: application/json" --header "Authorization: Token admin_token" --data '{"username": "customer@example.com" , "first_name": "Tony", "last_name": "Stark", "company_name":"Stark Industries", "password": "password"}'


## List Users (List)

Required Permissions: Admin

    curl https://twittnow.softlever.com/auth/users/ --header "Authorization: Token admin_token"


## Log user in (Generate Token)

    curl -X POST https://twittnow.softlever.com/auth/login/ --data '{"username": "customer@example.com" ,"password":"password"}' --header "Content-Type: application/json"


The generated token will expire in 30 days.


## Get a single user (Retrieve)

Required Permissions: User or Admin

    curl https://twittnow.softlever.com/auth/users/user_id/ --header "Authorization: Token user_token"


## Update User Details Partially (Partial Update)

Required Permissions: User or Admin

    curl -X PATCH https://twittnow.softlever.com/auth/users/user_id/ --header "Content-Type: application/json" --header "Authorization: Token user_token" --data '{"last_name": "Jarvis"}'


## Update all user details (Update)

Required Auth: User or Admin

    curl -X PUT https://twittnow.softlever.com/auth/users/user_id/ --header "Content-Type: application/json" --header "Authorization: Token user_token" --data '{"first_name": "Pepper", "last_name": "Pots", "username": "customer@example.com", "company_name": "The Stark Company"}'


## Log user out (Revoke token)

    curl -X POST https://twittnow.softlever.com/auth/logout/ --header "Content-Type: application/json" --header "Authorization: Token user_token"


## Log out of all sessions (Revoke all tokens)

    curl -X POST https://twittnow.softlever.com/auth/logout-all/ --header "Content-Type: application/json" --header "Authorization: Token user_token"


## Set a password for the user -> Useful for reset functionality

Required Permissions: User or Admin

    curl -X PATCH https://twittnow.softlever.com/auth/users/user_id/set-password/ --header "Content-Type: application/json" --header "Authorization: Token user_token" --data '{"password": "password"}'


## Delete a user

Required Permissions: Admin

    curl -X DELETE https://twittnow.softlever.com/auth/users/user_id/ --header "Content-Type: application/json" --header "Authorization: Token user_token"


## Adding Servicenow details for the authenticated user

Required Permissions: Self

    curl -X POST https://twittnow.softlever.com/servicenow-details/ --header "Content-Type: application/json" --header "Authorization: Token f988a990271bc66171eafd7091d681aedeccce3a1f4b03f3644a532dc74e2ae9" --data '{"instance_url": "https://dev119258.service-now.com", "admin_user": "admin", "admin_password": "dcyHPleT2F3C"}'


## Adding Servicenow details for another user

Required Permissions: Admin

    curl -X POST https://twittnow.softlever.com/servicenow-details/ --header "Content-Type: application/json" --header "Authorization: Token d4f74ff43e09c019f741b31a67e33dc933d314fadcfc5fb79f234ff9063bcabf" --data '{"instance_url": "https://dev119258.service-now.com", "admin_user": "admin", "admin_password": "dcyHPleT2F3C", "user": "a4279da2-e69d-495f-92ee-5ff59da4baf8"}'


If you receive this error; `{"user":["This field must be unique."]}` it means the specified user already has a Servicenow record.


## Listing Servicenow details

Required Permissions: Admin

    curl https://twittnow.softlever.com/servicenow-details/ --header "Content-Type: application/json" --header "Authorization: Token f988a990271bc66171eafd7091d681aedeccce3a1f4b03f3644a532dc74e2ae9"


## Get details for a single Servicenow record

Required Permissions: Self or Admin

    curl https://twittnow.softlever.com/servicenow-details/2/ --header "Content-Type: application/json" --header "Authorization: Token f988a990271bc66171eafd7091d681aedeccce3a1f4b03f3644a532dc74e2ae9"


## Updating Servicenow details partially

    curl -X PATCH https://twittnow.softlever.com/servicenow-details/2/ --header "Content-Type: application/json" --header "Authorization: Token f988a990271bc66171eafd7091d681aedeccce3a1f4b03f3644a532dc74e2ae9" --data '{"admin_user": "Twitter", "admin_password": "Y7Ifer3"}'


## Delete Servicenow details for a user

Required Permissions: Self or Admin

    curl -X DELETE https://twittnow.softlever.com/servicenow-details/3/ --header "Content-Type: application/json" --header "Authorization: Token f988a990271bc66171eafd7091d681aedeccce3a1f4b03f3644a532dc74e2ae9"


## Getting a twitter authentication URL

    curl https://twittnow.softlever.com/get-auth-url --header "Authorization: Token 5ffbb3c859b97cd634cfe4045669162360da4b0ac929165c38652abacdc34fa6"


## List all Twitter details

Required Permissions: Admin

    curl https://twittnow.softlever.com/twitter-details/ --header "Authorization: Token d4f74ff43e09c019f741b31a67e33dc933d314fadcfc5fb79f234ff9063bcabf"


## Retrieve Twitter details for a single user

    curl https://twittnow.softlever.com/twitter-details/1/ --header "Authorization: Token f988a990271bc66171eafd7091d681aedeccce3a1f4b03f3644a532dc74e2ae9"


## Unsubscribe from the authenticated user's Twitter

    curl -X DELETE https://twittnow.softlever.com/twitter-revoke/ --header "Authorization: Token 5793121eb47d82ee44b6f79b7032dd11c21c3c5d6c1dad291fc01649a795f88c"


## Create custom field
    
    curl -X POST https://twittnow.softlever.com/custom-fields/ --header "Content-Type: application/json" --header "Authorization: Token 2bd5a71c9498e235958dd99914d7820f0603c2719bb907d0fe01de800f6faa12" --data '{"field_name": "City" , "message": "Which city do you live in?"}'

## Retrieve custom fields

    curl https://twittnow.softlever.com/custom-fields/ --header "Authorization: Token 14da352fa342a30d5d8965e50076ea752acf0b73102dd08cd213bd068abc333a"

## Delete custom field

    curl -X DELETE https://twittnow.softlever.com/custom-fields/4/ --header "Content-Type: application/json" --header "Authorization: Token 5793121eb47d82ee44b6f79b7032dd11c21c3c5d6c1dad291fc01649a795f88c"

## Generate or Re-generate Twittnow developer token
Call this endpoint to generate a new token or revoke an existing one and recreate. The request body has to be emtpy. Twittnow won't expose any endpoint to view the current token.

    curl -X POST https://twittnow.softlever.com/api-key/ --header "Content-Type: application/json" --header "Authorization: Token 2bd5a71c9498e235958dd99914d7820f0603c2719bb907d0fe01de800f6faa12"

## Other endpoints

This section documents endpoints that will be used by Servicenow instances and Twitter. The only configuration needed on a servicenow instance is importing the required update set. The APIKey table also needs to have at least one API token, generated from the `/auth/login/` endpoint.


### Send a servicenow case event
    
    curl -X POST https://twittnow.softlever.com/events/ --header "Content-Type: application/json" --header "Authorization: Token user_token"

CURL is purely for illustrative purposes. These API call will actually run from a Servicenow instance.

### Receive events from Twitter

    https://twittnow.softlever.com/activity/

This endpoint receives account activity events from Twitter, processes messages if the activity is either a direct message or mention, then sends the results to the relevant Servicenow instance.

