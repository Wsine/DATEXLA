docker service create --network dockercoins --name redis cailloumajor/redis-armhf

for SERVICE in hasher rng worker; do
docker service create --network dockercoins --name $SERVICE dockercoins_$SERVICE
done

docker service create --network dockercoins --name webui --publish 8000:80 dockercoins_webui

