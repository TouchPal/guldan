#!/bin/bash

CONTAINERS=$(docker ps | grep 9092 | awk '{print $1}')
BROKERS=$(for CONTAINER in $CONTAINERS; do docker port $CONTAINER 9092 | sed -e "s/0.0.0.0:/$KAFKA_ADVERTISED_HOST_NAME:/g"; done)
echo $BROKERS | sed -e 's/ /,/g'
