#! /bin/bash

if [ -z $1 ]
then
  echo 'Synopsis:'
  echo
  echo 'post_comment.sh <credentials_file> <slide_id> [comment_text_file]'
  echo
  echo '<redentials_file> has to look like this:'
  echo "USERNAME='...'"
  echo "PASSWORD='...'"
  echo
  echo '<comment_text_file> contains the text to post as a comment'
  echo
  exit
fi

. $1
# test slide_id is 263
SLIDE_ID=$2

if [ "$3" = "" ]
then
  CONTENT="text=$(cat)"
else
  CONTENT="text@$3"
fi

# filename to use for stored cookies
COOKIES=cookies.txt

# where to post the comment
#HOST=https://nova.iguw.tuwien.ac.at
HOST=http://localhost:8000

# server configuration requires a valid (i.e. not malicious) referer
REFERER=${HOST}/

# file with CA to use for connection, alternatively use curl option '-k' for insecure connection
CERTS=certs

# the uri where this comment can be found (for bookmarking)
URI=${HOST}/slides/

# go to login page to fetch csrf token
curl --cacert ${CERTS} --referer ${REFERER} -v -c ${COOKIES} -b ${COOKIES} ${HOST}/gsi/login/

# extract csrftoken from cookie
CSRFTOKEN=$(grep csrftoke ${COOKIES} | awk '{print $7}')

# login to get a session id
curl --cacert ${CERTS} --referer ${REFERER} -X POST -v -c ${COOKIES} -b ${COOKIES} \
  -d "username=${USERNAME}&password=${PASSWORD}&remember=false&csrfmiddlewaretoken=${CSRFTOKEN}" \
  ${HOST}/gsi/signin/ 

# extract csrftoken from cookie
CSRFTOKEN=$(grep csrftoke ${COOKIES} | awk '{print $7}')

SLIDE_TYPE=25

# post content of ${COMMENT_TEXT_FILE} as a comment
curl --cacert ${CERTS} --referer ${REFERER} -X POST -v -c ${COOKIES} -b ${COOKIES} \
  -d "reference_type_id=${SLIDE_TYPE}&reference_id=${SLIDE_ID}&visibility=public" \
  -d "csrfmiddlewaretoken=${CSRFTOKEN}&reference_type_id=${SLIDE_TYPE}&reference_id=${SLIDE_ID}&visibility=public" \
  --data-urlencode "${CONTENT}" \
  --data-urlencode uri=${URI} \
  ${HOST}/comment/post/

