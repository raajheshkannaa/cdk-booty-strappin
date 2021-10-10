# CDK Bootstrapping at scale
Born out of love for AWS CDK.

Bootstrap all AWS Accounts and their regions under the AWS Organization and also add a trusted account which could further be the CI/CD or CDK Pipeline account from which automation is run later.

This will be a one time setup to be done which will immensly help in laying the foundation for Cross Account CDK Pipelines:heart:

### **Disclaimer**
_This automation process is one of the many many ways to accomplish the end result of bootstrapping all Accounts in an AWS Organization_

## Prerequisites
1. `cdk` should be preinstalled. If not run `npm install -g aws-cdk` in your terminal.
2. Have access to the AWS Organization Account with an IAM Role or user and those credentials set in the current shell before running this program.

## Workflow
* The program uses the AWS Organization AWS Profile credentials to `list_accounts` under the organization.
* This information is used to assume the `OrganizationAccountAccessRole` in each of those accounts`.
* Once a session is assumed, the session credentials are exported to the local shell.
* With the current shell environment variables set for the particular AWS Account, it goes ahead and bootstraps that account & every region in it.

## What is bootstrapping
Bootstrapping is basically a cloudformation template `CDKToolkit` which creates necessary resources such as s3 buckets, ecr registries, IAM roles, etc.. in place for further deployments using CDK.

## Usage
* Git clone repository `git clone https://github.com/raajheshkannaa/cdk-booty-strappin`
* If using an IAM User/role set AWS Organiztion profile in `~/.aws/credentials` file.
* If using SSO such as Okta for the AWS Orgnization account, use a program such as [`gimmeawscreds`](https://github.com/Nike-Inc/gimme-aws-creds) or [`saml2aws`](https://github.com/Versent/saml2aws) to obtain credentials and either set those as env variables or as a profile and export as `AWS_PROFILE=aws-org-profile`.
* Confirm credentials with `aws sts get-caller-identity`.
* Open the python file and add your `TRUSTED_ACCOUNT` variable to match your CI/CD pipeline AWS Account, so that it is trusted as a source for further CDK Deployments.
* Run `python3 cdk_bootstrap_multiple_accounts.py`

## Notes
* This python code will only bootstrap member AWS Accounts for an AWS Organization, does not bootstrap the Organization Master itself. Considering you have existing access, please bootstrap the Billing account using `cdk bootstrap --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess`
* The reason this needs to be run from the AWS Organization Account, is because it has existing trust relationships with all the member aws accounts with the `OrganizationAccountAccessRole`.
* This could also be run from the SecurityAudit account in the case when you have Control Tower setup and all AWS Accounts enrolled with the trust relationship setup for the `ControlTowerExecution` role.
* The reason why we use `subprocess` instead of `os` from python is because when a subsequent or multiple commands are run with os.system back to back, they are run in separate child shell processes, making it hard to export/set environment variables, that the code could then make use to assume IAM roles with.
* The reason for doing this python and shell fu is that `cdk bootstrap` currently is a cli command and gathering session information and storing credentials in memory with python provides flexibility with different platforms such as AWS Lambda, local environments such as Windows, Mac or Linux.
* This could technically be run as a lambda function(_not tested_) as well in the Organization Account whenever there is a new account is created, with help from CloudWatch Events. The Lambda function needs to be run with the OrganizationAccountAccessRole, after modifiying the trust of that role to be used by lambda to assume the role.
* Ideally I'm a big advocate of not running any resources in the AWS Organization Account and keep it locked as much as possible, however for the use case of accessing all memeber accounts from a central location is only possible from the Org account, until we establish the capability to do so from our Automation or Security Account after we establish a framework of necessary IAM Roles with trust relationships setup, like in a Control Tower environment.

