# TO-DO Items

### Documentation

* Introduction
* Architecture (w/ diagram)
* Provisioning Process (including manual steps)
* Troubleshooting
* Openstack smtp proxy

### Project

* GitHub repository (gdcorp-infosec) w/ permissions
* Cloud Readiness Review
* CICD - GitHub Actions
  - Infrastructure / Sceptre
  - Container build/deploy pipeline (Gophish)
  - Generate ServiceNow change orders when deploying to prod

### Current Exceptions

* App-level encryption of PII data (employee emails)
* Containers are not rotated every 24 hours
* Gophish logging does not use application security logging format

### Development

* TLS for traffic from ALB to Gophish
* Container/ECS scaling configuration
* Container rotation
* Adjust healthcheck intervals
* Unit test(s) (status lambda)

### Future

* Protect Gophish admin interface with SSO/JWT
* App-level encryption of PII data (employee emails)
* Expose Gophish metrics via CloudWatch
* Log/export status page matrics for dashboard visualization
* Application security logging for Gophish admin portal
* Links to additional resources/documentation on status page

