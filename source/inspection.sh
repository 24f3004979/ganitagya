#!/usr/bin/bash

for i in {1..10};do
	cat ../app.log;
	sleep 3s
done
echo "registration endpoint testing commands"
curl -X 'POST' \
  'http://localhost:8000/api/v1/register' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "string",
  "password": "string"
}'

echo "Login Testing sequence"
curl -X 'POST' \
  'http://localhost:8000/api/v1/login' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "string",
  "password": "string"
}'

