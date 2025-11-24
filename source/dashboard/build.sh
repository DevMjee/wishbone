aws ecr get-login-password --region eu-west-2 | \
docker login \
    --username AWS \
    --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com && \

docker buildx build --platform "linux/amd64" --provenance=false -t c20-wishbone-dashboard-ecr . && \
docker tag c20-wishbone-dashboard-ecr:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-dashboard-ecr:latest && \
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-dashboard-ecr:latest && \
aws ecs update-service --cluster c20-wishbone-ecs --service wishbone-dashboard-service --force-new-deployment --region eu-west-2