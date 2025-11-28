aws ecr get-login-password --region eu-west-2 | \
docker login \
    --username AWS \
    --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com && \

docker buildx build -f search_Dockerfile --platform "linux/amd64" --provenance=false -t c20-wishbone-search-ecr . && \
docker tag c20-wishbone-etl-ecr:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-search-ecr:latest && \
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-search-ecr:latest && \
aws lambda update-function-code \
           --function-name wishbone-search-lambda \
           --image-uri 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-search-ecr:latest
