#! /bin/bash

if [ -z $1 ]
then
  echo 'Synopsis:'
  echo
  echo 'post_comment.sh <credentials_file> <slide_filename> [comment_text_file]'
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

# where to post the comment
HOST=http://localhost:8000

# server configuration requires a valid (i.e. not malicious) referer
REFERER=${HOST}/

# the uri where this comment can be found (for bookmarking)
URI=${HOST}/slides/

# post content of ${COMMENT_TEXT_FILE} as a comment
curl --referer ${REFERER} -X POST -v \
  -d "secret=kalimero" \
  -d "filename=${SLIDE_ID}" \
  --data-urlencode "${CONTENT}" \
  --data-urlencode uri=${URI} \
  ${HOST}/comment/lecturer_post/

