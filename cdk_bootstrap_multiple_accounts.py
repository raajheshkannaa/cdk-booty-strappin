import boto3
import subprocess

# By default since code is run from the Organizations account, the account is trusted. Use this variable to add another account as trusted such as an Automation or Security account, from where CI/CD pipelines will be run. If you don't need or have a dedicated account, just use the Organization Account ID.
trusted_account = '<ENTER THE ACCOUNT ID YOU WILL RUN CI/CD PIPELINES FROM>' 

def get_org_accounts(session):
	org_client = session.client('organizations')

	results = []
	messages = []
	paginator = org_client.get_paginator('list_accounts')
	response_iterator = paginator.paginate()

	for response in response_iterator:
		results = results + response['Accounts']

	for index in results:
		messages = messages + (index['Id']).split()

	return messages

def assume_role(session, aws_account_number, role_name):
	resp = session.client('sts').assume_role(
		RoleArn='arn:aws:iam::{}:role/{}'.format(aws_account_number,role_name),
		RoleSessionName='CDKBootstrappin')
	
	# Storing STS credentials
	creds = boto3.Session(
		aws_access_key_id = resp['Credentials']['AccessKeyId'],
		aws_secret_access_key = resp['Credentials']['SecretAccessKey'],
		aws_session_token = resp['Credentials']['SessionToken']
	)

	print("Assumed session for {}.".format(
		aws_account_number
	))

	return creds, resp

if __name__ == '__main__':

	# Session credentials of current user and use this to assume roles.
	org_session = boto3.Session()
	accounts = get_org_accounts(org_session)

	# Get the current AWS Organization Account ID
	aws_org_account = boto3.client('sts').get_caller_identity()['Account']

	# Used to obtain the list of AWS Regions using the EC2 service.
	#ec2 = org_session.client('ec2', region_name='us-east-1')
	#regions = ec2.describe_regions()['Regions']
	
	for account in accounts:
		try:
			account = account.strip()

			# Session of the assumed IAM Role in the corresponding member account using the session(OrganizationAccountAccessRole/ControlTowerExecution) role.
			# If you have Control Tower enabled and necessary accounts enrolled, use `ControlTowerExecution` 
			# Under normal conditions this should be 'OrganizationAccountAccessRole'
			session, resp = assume_role(org_session, account, 'OrganizationAccountAccessRole') 
			
			
			# Credentials of the assumed role which will be used to set environment variables. 
			aws_access_key_id = str(resp['Credentials']['AccessKeyId'])
			aws_secret_access_key = str(resp['Credentials']['SecretAccessKey'])
			aws_session_token = str(resp['Credentials']['SessionToken'])

			# Iterate CDK Bootstrapping for all regions.
			# Comment out this `for` loop and Shift-Tab below section, if bootstrapping is not necessary for all regions.
			region_name = 'us-east-1' # Comment this out and un-comment lines 50-51 to enable bootstrapping for all regions.

			#for region in regions:
				#region_name = region['RegionName']

			'''
			Export environment variables
			* AWS_ACCESS_KEY_ID
			* AWS_SECRET_ACCESS_KEY
			* AWS_SESSION_TOKEN

			Execute `cdk bootstrap aws://<account>/<region> --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess --trust <CI/CD AWS Account>`
			'''
			command = "export AWS_ACCESS_KEY_ID=" + aws_access_key_id + ";export AWS_SECRET_ACCESS_KEY=" + aws_secret_access_key + ";export AWS_SESSION_TOKEN=" + aws_session_token + "; cdk bootstrap aws://" + account + "/" + region_name + " --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess --trust " + trusted_account
			
			# Execute the command in a single process shell.
			aws_cli = subprocess.run(command, shell=True)

		except Exception as e:
			print(e)
			pass