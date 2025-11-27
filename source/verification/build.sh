aws ecr get-login-password --region eu-west-2 | \
docker login \
    --username AWS \
    --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com && \

docker buildx build --platform "linux/amd64" --provenance=false -t c20-wishbone-verification-ecr . && \
docker tag c20-wishbone-tracking-tl-ecr:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-verification-ecr:latest && \
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-verification-ecr:latest && \
aws lambda update-function-code \
           --function-name wishbone-tracking-lambda \
           --image-uri 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c20-wishbone-verification-ecr:latest
