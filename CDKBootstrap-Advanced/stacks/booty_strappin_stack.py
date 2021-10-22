from typing import Pattern
from aws_cdk import (
	core,
	aws_events as events,
	aws_events_targets as targets,
	aws_lambda as _lambda,
	aws_iam as iam
)

from os import getcwd

from aws_cdk.aws_codestarnotifications import DetailType

class BootyStrappinStack(core.Stack):

	def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
		super().__init__(scope, construct_id, **kwargs)

		# Create a new IAM Role Policy which will be used by the Lambda to gather list of accounts from Organization and
		# assume a role in the new account either using OrganizationAccountAccessRole or AWSControlTowerExecution
		cdkbootstrap_role_policy = iam.ManagedPolicy(self, 'cdkbootstrap-policy',
			managed_policy_name='cdkbootstrap-policy',
			description='Policy for CDK Bootstrapping',
			statements = [
			iam.PolicyStatement(
			sid="CDKBootstrapPermissions",
			actions=[
				"sts:GetCallerIdentity",
				"iam:GetUser",
				"iam:ListRoles",
				"iam:ListAccountAliases",
				"organizations:ListAccounts"],
			effect=iam.Effect.ALLOW,
			resources=['*'],
			),
			iam.PolicyStatement(
				sid="AssumeRoleInTarget",
				effect=iam.Effect.ALLOW,
				actions=["sts:AssumeRole"],
				resources=["arn:aws:iam::*:role/OrganizationAccountAccessRole","arn:aws:iam::*:role/AWSControlTowerExecution"],
				conditions={
				"Bool": {
				  "aws:SecureTransport": "true"
					}
			  	}
				)
			]			
		)

		# Create the IAM Role
		cdkbootstrap_role = iam.Role(
			self, 'cdkbootstrap-role',
			role_name='cdkbootstrap-role',
			assumed_by=iam.CompositePrincipal(
				iam.ServicePrincipal('lambda.amazonaws.com'),
				iam.ServicePrincipal('ec2.amazonaws.com')
				)
		)
		# Attach the policy to the role
		cdkbootstrap_role_policy.attach_to_role(cdkbootstrap_role)
		# Attach necessary managed policies for Lambda execution
		cdkbootstrap_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaVPCAccessExecutionRole'))
		cdkbootstrap_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaRole'))

		# Absolute path of Dockerfile, cos this is needed for local developement and testing of the container image
		dockerfile=getcwd() + '/src'
		# Lambda Docker Container 
		bootystrap = _lambda.DockerImageFunction(
			self, 'CDKBootyStrap',
			function_name='CDKBootStrapAutomation',
			code=_lambda.DockerImageCode.from_image_asset(dockerfile),
			timeout=core.Duration.seconds(900),
			memory_size=128,
			role=cdkbootstrap_role,
		)

		# AWS CloudTrail API call as the EventPattern to trigger the lambda 
		rule = events.Rule(
			self, 'TriggerCDKBootStrapping',
			rule_name='TriggerCDKBootStrapping',
			event_pattern=events.EventPattern(
				source=['aws.organizations'],
				detail_type=['AWS Service Event via CloudTrail'],
				detail={
					"eventSource": ["organizations.amazonaws.com"],
					"eventName": ["CreateAccountResult"]
				}
			)
		)
		
		# Point the Event Rule to the our Lambda
		rule.add_target(targets.LambdaFunction(bootystrap))
