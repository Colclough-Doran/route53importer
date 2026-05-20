AWS Route53 to Terraform Import Script

1. Overview
This Python script automates the process of importing AWS Route53 DNS records into Terraform configuration files. It downloads Route53 hosted zone records, converts them into Terraform-compatible syntax, and generates the necessary Terraform files and import scripts.

2. Prerequisites
- Python 3.x
- AWS CLI installed and configured with the appropriate profile
- Terraform 1.5.7 or higher
- Required AWS IAM permissions to list Route53 records

3. Configuration
Before running the script, update the following variables at the top of the script:
- hosted_zone_id: The AWS Route53 Hosted Zone ID
- hosted_zone_name: The name of the hosted zone
- aws_profile: The AWS CLI profile to use for authentication
- aws_region: The AWS region for the hosted zone
- project_name: The name of the Terraform project
- login_profile: The AWS CLI profile to use for downloading Route53 records

4. Usage
4.1. Run the Script
Execute the script using Python:
python route53_to_terraform.py

4.2. Output Files
The script generates the following files in a directory named after the hosted zone:
- locals.tf: Terraform locals configuration
- provider.tf: AWS provider and Terraform backend configuration
- tags.tf: Terraform tags module configuration
- <hosted_zone_name>_hosted_zone.tf: Terraform resource definitions for Route53 records
- import-<hosted_zone_name>.sh: Bash script for importing existing resources into Terraform state

5. Workflow
5.1. Create Terraform Project Structure
The script creates the necessary directory and Terraform files (locals.tf, provider.tf, tags.tf) if they do not already exist.

5.2. Download AWS Route53 Records
The script downloads the Route53 records for the specified hosted zone and saves them as a JSON file.

5.3. Convert and Generate Terraform Files
The script reads the JSON file, converts the Route53 records into Terraform syntax, and writes them to the appropriate .tf files.

5.4. Generate Import Script
The script generates a bash script (import-<hosted_zone_name>.sh) containing the necessary terraform import commands to import existing Route53 resources into Terraform state.

6. Running the Import Script
After generating the Terraform files, run the import script to import the existing Route53 resources into Terraform state:
cd <hosted_zone_directory>
chmod +x import-<hosted_zone_name>.sh
./import-<hosted_zone_name>.sh

7. Applying Terraform Changes
After importing the resources, apply the Terraform configuration to ensure the state matches the actual infrastructure:
terraform plan
terraform apply

8. Features
- Handles standard, weighted, multi-value, and alias Route53 records
- Converts special characters in record names to Terraform-compatible formats
- Generates Terraform files and import scripts automatically
- Idempotent: Only creates files if they do not already exist

9. Limitations
- The AWS Route53 API has rate limits. If you exceed these limits, your connection may be throttled.
- The script currently processes one hosted zone at a time.
- Some complex record configurations may require manual adjustments in the generated Terraform files.

10. Error Handling
The script includes basic error handling and will print error messages to the console if issues arise. Check the console output for details if the script fails.

11. License
This script is provided as-is without any warranty. Use at your own risk.