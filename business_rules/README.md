**NOTE**: Always make sure you are in the same application scope when doing everything below.


# STEP 1: Create a REST MESSAGE

`REST MESSAGE -> NEW`

Name: Twitter DM

Endpoint: https://sntwitter.softlever.com/api/events

`Http Methods -> New Method`

Name: Send Message

Http Method: POST

Endpoint: https://sntwitter.softlever.com/api/events


`Variable Substituitions -> New`

1. name -> message, test_value -> test message

2. name -> target, test_value -> 0000000

3. name -> user_id, test_value -> {The user id on your dashboard. Example 3c6k57a3-791a-4d11-93b2-cc9561c1ecz1}


`Http Request -> Content`

message=${message}&target=${target}&user_id=${user_id}


`Http Headers`

1. Content-Type -> application/x-www-form-urlencoded


# STEP 2: Create a Business Rule

`Business Rules -> New`

Name: Send Twitter Direct Message

Table: sn_customerservice_case

When to Run: after update

Order: 200

Filter Conditions: Additional Comments, Changes


## Role Conditions

It's important to differentiate comments published by customer support agents and those created by the customer from Twitter. We will use role conditions to trigger the BR only when a non-customer user publishes a comment. To do this, edit `Role Conditions`

Select all roles that you want to have the ability to send comments to Twitter. `DO NOT` select `csm_ws_integration`. This is the role that identifies the customer user. In fact, whenever possible, assign a specific role to users who are allowed to use this feature.

If you don't apply role conditions properly, the BR will send back messages created from mentions and direct messages. So you have to get this part right.


## Finally...

Advanced -> Copy the contents of `business_rules/send_dm.js`

Remember to replace `your_user_id_here` with your own user ID. You can get this on he dashboard.
