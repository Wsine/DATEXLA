for SERVICE in redis hasher rng webui worker;do
docker service rm $SERVICE
done
