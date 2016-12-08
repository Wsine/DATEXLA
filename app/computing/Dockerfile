FROM datexla/test:v2

MAINTAINER haoxian tan "tamhoin@gmail.com"

#load env
ENV HADOOP_HOME /home/downloads/hadoop-2.7.3
ENV HADOOP_CONFIG $HADOOP_HOME/etc/hadoop
ENV PATH $PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV SPARK_HOME /home/downloads/spark-2.0.1-bin-hadoop2.7
ENV PATH $PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV HADOOP_ROOT_LOGGER INFO,console

EXPOSE 4040 8080 50070 50075 50090 50105 50030 50060 60010 60030
ENTRYPOINT ["/bin/bash","-c","service ssh start && sleep 500000000"]
