
**To install aws in Linux**
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html


The cluster will be installed by default in us-east-1 region. If you want to deploy it in different region please change it in varianles.tf file and following commands accordingly.




**You do not need to have a user in IAM necessarily, however if you have could be better**
  
I used temporary SSO access here.



**to connect to AWS through cli:**
```
$ aws configure
AWS Access Key ID [None]: AXXXXXXXXXXXXXXXXXXR
AWS Secret Access Key [None]: CXXXXXXXXXXXXXXXXXXXXXXXXXXXXs
Default region name [None]: us-east-1
Default output format [None]: 
hrouhan@hrz aws $ aws iam list-users
```

  > The cluster will be deployed by default in us-east-1 region which has been configigured in variables.tf

To avoid any unforseen error please export following environmental variable in your terminal before starting with the Terraform

$ export AWS_REGION=us-east-1

**Then simply initialize the terraform and apply**
```
$ terraform init -upgrade
$ terraform apply -auto-approve
```

**After you are done, please destroy everthing**
```
terraform destroy -auto-approve
```


  > in case the destroy process got stocked which is normal in EKS, try to delete from portal in following order:
      load balancer
      VPC
      network interfaces

**all pods will be deployed in security-team namespace**

  
  > some useful commands

    
    kubectl get pods -A
    
    for deleting any pods, you need to delete the corresponding deployments

    kubectl get deployments -A
    kubectl delete deployment nginx-demo
    

After deploying the cluster, you might need to check the pods/nodes directly from console (logged with your user). 

Important:

  There are several commands inserted into the 06-others.tf file for fully automation. The commands are partially **aws** commands which for execution/connection are dependent on proper "AWS_REGION" configuration in your terminal. Therefore make sure before running the Terraform commands, the environment variable has been set correctly. 
    > if you forgotten to set it in the first round of the Terraform execution, you need to detroy the cluster and re-create/re-apply it again since the commands in the 06-others.tf file will be executed only One time in cluster creation and not in the minor modification. Another option would be to deploy the commands in the 06-others.tf manually!




