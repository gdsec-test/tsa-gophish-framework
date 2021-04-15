# PhishFramework Introduction

GoDaddy utilizes the [Gophish](https://getgophish.com/) software to conduct
security exercises that measure the effectiveness of phishing awareness
training for GoDaddy employees.  The Gophish software allows an administrator
to create campaigns which result in phishing emails sent to a targeted list of
employees.  Statistics are then collected that show how many employees opened
the phishing email, how many clicked the link in the email, how many provided
credentials, etc.

This infrastructure was previously configured in an ad-hoc manner.  This
project attempts to formalize the infrastructure as a maintainable stack using
GoDaddy best practices for AWS-based projects.

This project provides two primary interfaces for users, which are described
more thoroughly in the [Architecture Documentation](ARCHITECTURE.md):

* The **admin** interface, which allows administrators to manage campaigns and
  related configuration settings

* The **status** interface, which GoDaddy employees can use to determine if a
  security exercise is currently in progress
