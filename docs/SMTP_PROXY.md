# SMTP Proxy

While not technically required for a Gophish installation, GoDaddy networking
infrastructure may limit SMTP traffic originating from the PhishFramework AWS
account.  In this case, using a SMTP proxy may be desired.  This SMTP proxy
configuration describes how an Openstack instance on-premise can be used for
outbound email traffic.

### OpenStack

1. Use [Cloud UI](https://cloud.int.godaddy.com/networking/securitygroups/list)
   to create a `smtp` security group that will be used by the OpenStack VM,
   with the following IPv4 rules:

   | Direction | Protocol | Port Range | Source / Destination |
   |-----------|----------|------------|----------------------|
   | Ingress   | TCP      | 25         | 10.0.0.0/8           |

1. Use [Cloud UI](https://cloud.int.godaddy.com/compute/vms) to create a VM.
   These steps assume that a `tsa` effort and `tsa` OpenStack project already
   exist, and that the Floating IP `10.32.156.220` has been created prior to
   the VM being created.  The following configuration values were used for the
   existing `tsa-smtp-proxy` VM:

   | Setting       | Value                                |
   |---------------|--------------------------------------|
   | FQDN          | `tsa-smtp-proxy.cloud.phx3.gdg`      |
   | Floating IP   | `10.32.156.220`                      |
   | Firewall Rule | `smtp`                               |
   | Size          | `m1.small`                           |
   | Image         | `centos7-base-20210309a-0.0.8-3.el7` |

### On-box Network Configuration

1. Connect to the `tsa-smtp-proxy` virtual machine, and execute the following
   commands to bind the floating IP:

   ```
   yum -y install monitoring-scripts
   /opt/monitoring/bin/openstack-vm-networking.sh bind -f 10.32.156.220 -s -p
   yum -y remove monitoring-scripts
   ```

1. Execute the following commands to enable forwarding across network
   interfaces:

   ```
   echo "net.ipv4.ip_forward = 1" > /etc/sysctl.d/ip_forward.conf
   systemctl restart systemd-sysctl
   ```

1. Execute the following commands to enable forwarding of network traffic
   received on port 25 to **p3plemlrelay-v01.prod.phx3.secureserver.net**
   (`184.168.130.211`):

   ```
   iptables -t nat -A PREROUTING -p tcp --dport 25 -j DNAT --to-destination 184.168.130.211:25
   iptables -t nat -A POSTROUTING -j MASQUERADE
   service iptables save
   ```

### Automatic Patching

The [yum-cron](https://github.secureserver.net/IPE/yum-cron) GitHub repository
contains scripts that can be used to perform automated patching with reboots as
required.

1. Create the file `/etc/cron.daily/01-yum` with the following content:

   ```
   #!/bin/sh
   # Run a yum update daily so we are always up-to-date
   RAND=$(awk 'BEGIN { srand(); print int(rand()*600) }')
   /bin/sleep "${RAND}"s
   /bin/yum update -y
   ```

1. Create the file `/etc/cron.daily/zz-uname-check` with the following content:

   ```
   #!/bin/sh
   #Check to see if running kernel is same as most recently installed kernel - reboot if not
   running_kernel=$(/bin/uname -r)
   installed_kernel=$(/bin/rpm -q kernel --last | /bin/awk '{print $1}' | /bin/head -n 1 | /bin/sed s/kernel-//g)
   if [ "${installed_kernel}" != "${running_kernel}" ]
     then RAND=$(/bin/awk 'BEGIN { srand(); print int(rand()*600) }')
     /bin/sleep $(( RAND % 600 + 1 ))s && /bin/echo "$(date) - Reboot to make kernel work" >> /var/log/kernel-reboot.log
     /sbin/reboot -n
   fi
   ```
