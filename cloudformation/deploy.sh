#!/usr/bin/env bash
STACK_NAME="gpoc-stack"
LAMBDA_VERSION="1.0"
POCSTAGE="dev"
DEFAULT_PYTHON_RUNTIME="python3.8"
NOW=$(date "+%Y%m%d_%H%M%S")
CODE_S3_PREFIX=${NOW}
CODE_UPLOAD_BUCKET="greengrass-poc-buck"
REGION="us-east-1"
CODE_S3_PREFIX="${CODE_S3_PREFIX}.gpoc-function"

CODE_ZIP="function.zip"

upload() {
    rm ./cloudformation/${CODE_ZIP}
    cd ./lambda/api

    pip3 install -r ./requirements.txt --target ./
    zip -r ../../cloudformation/${CODE_ZIP} .

    cd ../../cloudformation
    ls
    aws --region ${REGION} s3 cp ${CODE_ZIP} s3://${CODE_UPLOAD_BUCKET}/${CODE_S3_PREFIX}/${CODE_ZIP}

}
deploy() {

    aws --region ${REGION} cloudformation deploy \
        --template-file cf-template.yaml \
        --s3-bucket ${CODE_UPLOAD_BUCKET} \
        --s3-prefix ${CODE_S3_PREFIX} \
        --stack-name ${STACK_NAME} \
        --capabilities CAPABILITY_NAMED_IAM \
        --no-fail-on-empty-changeset \
        --parameter-overrides \
        LambdaCodeS3Bucket=${CODE_UPLOAD_BUCKET} \
        LambdaCodeS3Key="${CODE_S3_PREFIX}/${CODE_ZIP}" \
        PocStageName=${POCSTAGE} \
        PythonRuntime=${DEFAULT_PYTHON_RUNTIME}
}
upload && deploy
