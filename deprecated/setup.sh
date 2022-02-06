#!/bin/bash
echo "Pulling project from Github"
git pull origin master

# Check if env file exists
# If not, create from user input
if [ -e .env ]
then
    echo "env file already exists"
else
	echo "Collecting runtime variables. Input required"

	echo "Django"

	read -p "Django Secret Key: " SECRET_KEY
	read -p "Django Allowed Hosts (Space separated): " ALLOWED_HOSTS

	echo "Servicenow"

	read -p "Servicenow Instance URL: " SERVICENOW_URL
	read -p "Servicenow Admin User: " SERVICENOW_USER
	read -p "Servicenow Admin Password: " SERVICENOW_PWD

	read -p "Servicenow Customer Account ID: " SERVICENOW_CUSTOMER_ACCOUNT
	read -p "Servicenow Customer Account Password: " SERVICENOW_CUSTOMER_ACCOUNT_PWD
	read -p "Servicenow Customer Account Sys ID: " SERVICENOW_CUSTOMER_SYS_ID

	read -p "Servicenow Case Account: " SN_TWITTER_CASE_ACCOUNT

	echo "Twitter Developer"

	read -p "Twitter Consumer Key (API Key): " CONSUMER_KEY
	read -p "Twitter Consumer Secret (API secret): " CONSUMER_SECRET
	read -p "Twitter Callback URL: " CALLBACK_URL
	read -p "Twitter User ID: " TWITTER_USER_ID
	read -p "Twitter Handle: " TWITTER_USERNAME


	echo "Writing variables to env file"

	printf "SECRET_KEY=$SECRET_KEY\n" >> .env
	printf "DEBUG=0\n" >> .env
	printf "ALLOWED_HOSTS=$ALLOWED_HOSTS\n" >> .env

	printf "SERVICENOW_URL=$SERVICENOW_URL\n" >> .env
	printf "SERVICENOW_USER=$SERVICENOW_USER\n" >> .env
	printf "SERVICENOW_PWD=$SERVICENOW_PWD\n" >> .env

	printf "SERVICENOW_CUSTOMER_ACCOUNT=$SERVICENOW_CUSTOMER_ACCOUNT\n" >> .env
	printf "SERVICENOW_CUSTOMER_ACCOUNT_PWD=$SERVICENOW_CUSTOMER_ACCOUNT_PWD\n" >> .env
	printf "SERVICENOW_CUSTOMER_SYS_ID=$SERVICENOW_CUSTOMER_SYS_ID\n" >> .env
	printf "SN_TWITTER_CASE_ACCOUNT=$SN_TWITTER_CASE_ACCOUNT\n" >> .env

	printf "CONSUMER_KEY=$CONSUMER_KEY\n" >> .env
	printf "CONSUMER_SECRET=$CONSUMER_SECRET\n" >> .env
	printf "CALLBACK_URL=$CALLBACK_URL\n" >> .env
	printf "TWITTER_USER_ID=$TWITTER_USER_ID\n" >> .env
	printf "TWITTER_USERNAME=$TWITTER_USERNAME\n" >> .env

fi

echo "Stopping running containers" # if already running
sudo docker-compose down

# Build image and run container
echo "Running containers"
sudo docker-compose up --build -d

echo "Updating database tables"
sudo docker-compose exec web python manage.py migrate

# Check if cron jobs exist,
# if either of them are absent create both
crontab -l > cron_bkp

twitter_cron=$(sed -n "/docker exec servicenow-twitter_web_1 python manage.py twitter/p" cron_bkp)
servicenow_cron=$(sed -n "/docker exec servicenow-twitter_web_1 python manage.py servicenow/p" cron_bkp)

if [[ $twitter_cron == "" || $servicenow_cron == "" ]]
then
	echo "Creating Cron Jobs"
	echo "*/3 * * * * docker exec servicenow-twitter_web_1 python manage.py twitter" >> cron_bkp
	echo "*/5 * * * * docker exec servicenow-twitter_web_1 python manage.py servicenow" >> cron_bkp
	crontab cron_bkp
	rm cron_bkp
fi

echo "Starting mentions stream"
sudo docker-compose exec -T web python manage.py stream_mentions &