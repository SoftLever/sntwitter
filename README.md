# FUNCTIONALITY OVERVIEW

The following flowchart shows how the program works at a basic level

![Flowchart](/docs/servicenow_twitter_flowchart.jpeg "Flowchart")


# INITIAL SETUP

Pull this project and follow the steps below.


## 1. Django

Generate a strong secret key for your django app and store it in `SECRET_KEY`

Store your ip address or domain name in `ALLOWED_HOSTS`

## 2. ServiceNow (Per User)

### Create New User

In order to differentiate messages sent from Twitter by customers and those sent from ServiceNow, we will need to create a new user. To create a new user in ServiceNow, go to `User Administration` -> `Users` -> `New`

Save the user ID and password in `SERVICENOW_CUSTOMER_ACCOUNT` and `SERVICENOW_CUSTOMER_ACCOUNT_PWD` environment variables.

Assign `csm_ws_integration` role to the user.

Copy the user sys_id to `SERVICENOW_CUSTOMER_SYS_ID`. You can get the sys_id by navigating to `user menu` -> `Copy sys_id`


## Custom Case Fields

We need a way of differentiating cases opened on twitter. For this, we'll create a custom field called `twitter_user_id` of type `string` and length `40` in the Case form. Follow [this](https://docs.servicenow.com/bundle/rome-platform-administration/page/administer/field-administration/task/t_CreatingNewFields.html) guide

![Custom twitter ID](/docs/twitter_id.gif "Custom twitter id field")


Repeat the step above for a field called `twitter_username`


## 3. Twitter Developer

### Callback URL

This is required by Twitter to complete OAuth1.0a. You must whitelist the URL to which the user will be redirected after authentication.

You must also add the callback url in the `CALLBACK_URL` environment variable.

The callback url should be `https://example.com/addtwitteraccount/confirm/`

### Twitter APP Keys

`CONSUMER_KEY`

`CONSUMER_SECRET`


## Build

    docker-compose up --build -d
