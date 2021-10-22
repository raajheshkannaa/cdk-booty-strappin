FROM public.ecr.aws/lambda/python:3.9

# Install OS Packages needed for running `npm`
RUN yum install -y gcc-c++ make 
RUN curl -sL https://rpm.nodesource.com/setup_16.x | bash - 
RUN yum install -y nodejs 
RUN npm install -g aws-cdk
RUN mkdir -p /var/task/cdk.out

# Copy function code
COPY app.py cdk.json bootystrappin.py ${LAMBDA_TASK_ROOT}

# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "bootystrappin.main" ]