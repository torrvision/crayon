FROM tensorflow/tensorflow
RUN pip install flask
ADD startup.sh /
ADD server.py /
EXPOSE 8889
# TODO: move from cmd to entrypoint
CMD /bin/sh /startup.sh