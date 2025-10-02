#!/bin/bash
# Create the user SSH directory, just in case.
GENIUSER=`geni-get user_urn | awk -F+ '{print $4}'`
if [ $? -ne 0 ]; then
echo "ERROR: could not run geni-get user_urn!"
exit 1
fi

# Setup password-less ssh between nodes
if [ "$GENIUSER" = "root" ]; then
    ssh_dir=/root/.ssh
else
    ssh_dir=/users/$GENIUSER/.ssh
fi
sudo su - $GENIUSER -c "mkdir ${ssh_dir} && chmod 700 ${ssh_dir}"
sudo su - $GENIUSER -c "/usr/bin/geni-get key > ${ssh_dir}/id_rsa"
sudo su - $GENIUSER -c "chmod 600 ${ssh_dir}/id_rsa"
sudo su - $GENIUSER -c "chown $GENIUSER: ${ssh_dir}/id_rsa"
sudo su - $GENIUSER -c "ssh-keygen -y -f ${ssh_dir}/id_rsa > ${ssh_dir}/id_rsa.pub"
sudo su - $GENIUSER -c "cat ${ssh_dir}/id_rsa.pub >> $ssh_dir/authorized_keys2"
sudo su - $GENIUSER -c "echo -e '\\nHost * \\n\\tStrictHostKeyChecking no\\n' >> ${ssh_dir}/config"
sudo su - $GENIUSER -c "chmod 644 ${ssh_dir}/config"
