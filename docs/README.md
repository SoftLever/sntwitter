# TwittNow API Documentation

## User Account Configurations

### Create a new user

Required Permissions: Admin

    curl -X POST https://twittnow.softlever.com/auth/users/ --header "Content-Type: application/json" --header "Authorization: Token admin_token" --data '{"username": "customer@example.com" , "first_name": "Tony", "last_name": "Stark", "company_name":"Stark Industries", "password": "password"}'


### Log user in (Generate Token)

    curl -X POST https://twittnow.softlever.com/auth/login/ --data '{"username": "customer@example.com" ,"password":"password"}' --header "Content-Type: application/json"


The generated token will expire in 24 hours.

### Update User Details Partially (Partial Update)

Required Permissions: User or Admin

    curl -X PATCH https://twittnow.softlever.com/auth/users/user_id/ --header "Content-Type: application/json" --header "Authorization: Token user_token" --data '{"last_name": "Jarvis"}'


### Log user out (Revoke token)

    curl -X POST https://twittnow.softlever.com/auth/logout/ --header "Content-Type: application/json" --header "Authorization: Token user_token"


### Log out of all sessions (Revoke all tokens)

    curl -X POST https://twittnow.softlever.com/auth/logout-all/ --header "Content-Type: application/json" --header "Authorization: Token user_token"


### Set a password for the user -> Useful for reset functionality

Required Permissions: User or Admin

    curl -X PATCH https://twittnow.softlever.com/auth/users/user_id/set-password/ --header "Content-Type: application/json" --header "Authorization: Token user_token" --data '{"password": "password"}'


## Servicenow Configurations

### Adding Servicenow details for the authenticated user

    curl -X POST https://twittnow.softlever.com/servicenow-details/ --header "Content-Type: application/json" --header "Authorization: Token 08f4be707cc895fc3c882406d3472fc2a1d843e49ac38ca4e92dbfcfda1a8a82" --data '{"instance_url": "https://dev119258.service-now.com", "admin_user": "admin", "admin_password": "dcyHPleT2F3C"}'


If you receive this error; `{"user":["This field must be unique."]}` it means the user already has a Servicenow record.


## Get Servicenow details

    curl https://twittnow.softlever.com/servicenow-details/ --header "Content-Type: application/json" --header "Authorization: Token 08f4be707cc895fc3c882406d3472fc2a1d843e49ac38ca4e92dbfcfda1a8a82"


## Updating Servicenow details partially

    curl -X PATCH https://twittnow.softlever.com/servicenow-details/2/ --header "Content-Type: application/json" --header "Authorization: Token 08f4be707cc895fc3c882406d3472fc2a1d843e49ac38ca4e92dbfcfda1a8a82" --data '{"admin_user": "Twitter", "admin_password": "Y7Ifer3"}'


## Delete Servicenow details

    curl -X DELETE https://twittnow.softlever.com/servicenow-details/2/ --header "Content-Type: application/json" --header "Authorization: Token 08f4be707cc895fc3c882406d3472fc2a1d843e49ac38ca4e92dbfcfda1a8a82"


## Getting a twitter authentication URL

    curl https://twittnow.softlever.com/get-auth-url --header "Authorization: Token 08f4be707cc895fc3c882406d3472fc2a1d843e49ac38ca4e92dbfcfda1a8a82"


## Retrieve Twitter details

    curl https://twittnow.softlever.com/twitter-details/ --header "Authorization: Token 08f4be707cc895fc3c882406d3472fc2a1d843e49ac38ca4e92dbfcfda1a8a82"


## Unsubscribe from the authenticated user's Twitter

    curl -X DELETE https://twittnow.softlever.com/twitter-revoke/ --header "Authorization: Token 08f4be707cc895fc3c882406d3472fc2a1d843e49ac38ca4e92dbfcfda1a8a82"


## Create custom field
    
    curl -X POST https://twittnow.softlever.com/custom-fields/ --header "Content-Type: application/json" --header "Authorization: Token 08f4be707cc895fc3c882406d3472fc2a1d843e49ac38ca4e92dbfcfda1a8a82" --data '{"field_name": "City" , "message": "Which city do you live in?"}'

## Retrieve custom fields

    curl https://twittnow.softlever.com/custom-fields/ --header "Authorization: Token 08f4be707cc895fc3c882406d3472fc2a1d843e49ac38ca4e92dbfcfda1a8a82"

## Delete custom field

    curl -X DELETE https://twittnow.softlever.com/custom-fields/4/ --header "Content-Type: application/json" --header "Authorization: Token 5793121eb47d82ee44b6f79b7032dd11c21c3c5d6c1dad291fc01649a795f88c"

## Generate or Re-generate Twittnow developer token
Call this endpoint to generate a new token or revoke an existing one and recreate. The request body has to be emtpy. Twittnow won't expose any endpoint to view the current token.

    curl -X POST https://twittnow.softlever.com/api-key/ --header "Content-Type: application/json" --header "Authorization: Token 546c2b66c59ce28e56f9f7c37abe426c04802028956920199c25e1babfc08fa7"

