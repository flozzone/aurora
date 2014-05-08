#! /bin/bash

COOKIES=cookies.txt
USERNAME=qq
PASSWORD=foobar
HOST=http://localhost:8000

# go to login page to fetch csrf token
curl -v -c ${COOKIES} -b ${COOKIES} ${HOST}/login/

# extract csrftoken from cookie
CSRFTOKEN=$(grep csrftoke ${COOKIES} | awk '{print $7}')

# login to get a session id
curl -X POST -v -c ${COOKIES} -b ${COOKIES} \
  -d "username=${USERNAME}&password=${PASSWORD}&remember=false&csrfmiddlewaretoken=${CSRFTOKEN}" \
  ${HOST}/signin/ 

SLIDE_TYPE=27

# set the slide id to post to here
SLIDE_ID=263
COMMENT_TEXT_FILE=comment_text

# post content of ${COMMENT_TEXT_FILE} as a comment
curl -X POST -v -c ${COOKIES} -b ${COOKIES} \
  -d "csrfmiddlewaretoken=${CSRFTOKEN}&reference_type_id=${SLIDE_TYPE}&reference_id=${SLIDE_ID}&visibility=public" \
  --data-urlencode text@${COMMENT_TEXT_FILE} \
  --data-urlencode uri=${HOST}/slides/ \
  ${HOST}/post_comment/
