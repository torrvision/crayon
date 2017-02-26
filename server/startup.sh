#!/bin/bash

# Default values for the arguments
CRAYON_FRONTEND_RELOAD="$1"
if [[ $CRAYON_FRONTEND_RELOAD == "" ]]; then
    CRAYON_FRONTEND_RELOAD="10"
fi

CRAYON_BACKEND_RELOAD="$2"
if [[ $CRAYON_BACKEND_RELOAD == "" ]]; then
    CRAYON_BACKEND_RELOAD="0.5"
fi

# Try to patch tensorboard to reduce autorefresh time and allow subsecond backend refresh
python /patch_tensorboard.py "$CRAYON_FRONTEND_RELOAD" "$CRAYON_BACKEND_RELOAD"
RETURN_CODE="$?"

# If path failed, set backend reload to integer
if [[ ${RETURN_CODE} != "3" ]] && [[ ${RETURN_CODE} != "2" ]]; then
    CRAYON_BACKEND_RELOAD="1"
fi
echo "Using $CRAYON_BACKEND_RELOAD for backend reload time."

tensorboard --reload_interval $CRAYON_BACKEND_RELOAD --logdir /tmp/tensorboard --port 8888 &

python /server.py 8889 $CRAYON_BACKEND_RELOAD 2>&1 1>/tmp/crayon.log
