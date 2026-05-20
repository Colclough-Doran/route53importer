
import json, os
### Hosted Zone variables ###
hosted_zone_id = '<<HOSTED_ZONE_ID>>' # This needs to be changed for each hosted zone
hosted_zone_name = '<<HOSTED_ZONE_NAME' # This needs to be changed for each hosted zone
##### Project variables #####
aws_profile = '<<AWS_PROFILE_NAME>>' # used in provider.tf
aws_region = '<<AWS_REGION>>' # used in provider.tf
project_name = '<<TERRAFORM_PROJECT_NAME">>' # used in provider.tf
aws_service = 'route53' # used in provider.tf
login_profile = '<<AWS_PROFILE_NAME>>' # used to log in and download route53 records
#############################
hosted_zone_file_name = hosted_zone_name.replace('.', '-')
hosted_zone_function = hosted_zone_name.replace('.', '_')
#############################
dir_path = hosted_zone_file_name
terraform_file_name = '{0}_hosted_zone.tf'.format(hosted_zone_file_name)
terraform_import_file_name = 'import-{0}.sh'.format(hosted_zone_file_name)
json_file_name = 'hosted-zone-{0}.json'.format(hosted_zone_file_name)
#############################
class Route53Import():
# Calls the Terraform file creation functions
    def create_terraform_project_structure(): 
        # If the files do not exist then the create function for that file will be called
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            if not os.path.exists(os.path.join(dir_path, 'locals.tf')):
                Route53Import.create_terraform_project_file_locals()
            if not os.path.exists(os.path.join(dir_path, 'provider.tf')):
                Route53Import.create_terraform_project_file_provider()
            if not os.path.exists(os.path.join(dir_path, 'tags.tf')):
                Route53Import.create_terraform_project_file_tags()
        except Exception as e:
            print('create_terraform_project_structure\n', e)
# Creates the Terraform locals file
    def create_terraform_project_file_locals(): 
        try:           
            data = open(os.path.join(dir_path, 'locals.tf'), 'w')
            
            data.write(
                '''locals { \
                \n\tservice = "route53" \
                \n\tenvironment = "live" \
                \n}''')
            
            data.close()
        except Exception as e:
            print('create_terraform_project_file_locals\n', e)
# Creates the provider locals file
    def create_terraform_project_file_provider(): 
        try:
            data = open(os.path.join(dir_path, 'provider.tf'), 'w')
            data.write(
                '''provider "aws" {{ \
                \n\tprofile = "{0}" \
                \n\tregion  = "{1}" \
                \n
                \n\tdefault_tags {{ \
                \n\t\ttags = module.tags_local.tags \
                \n\t}} \
                \n}} \
                \n \
                \nterraform {{ \
                \n\trequired_version = ">= 1.5.7" \
                \n\tbackend "s3" {{ \
                \n\t\tkey            = "{2}/{3}-{4}/terraform.tfstate" \
                \n\t\tbucket         = "terraform-state-{0}" \
                \n\t\tprofile        = "{0}" \
                \n\t\tdynamodb_table = "terraform-state-management" \
                \n\t\tregion         = "{1}" \
                \n\t}} \
                \n}}'''.format(aws_profile, aws_region, project_name, aws_service, hosted_zone_file_name)
            )
            data.close()
        except Exception as e:
            print('create_terraform_project_file_provider\n', e)
# Creates the Terraform tags file
    def create_terraform_project_file_tags(): 
        try:
            data = open(os.path.join(dir_path, 'tags.tf'), 'w')
            data.write(
                '''module "tags_local" { \
                \n\tsource = "../../../../modules/tags" \
                \n\n\tenvironment = local.environment \
                \n\tapplication = local.application \
                \n}'''
            )
            data.close()
        except Exception as e:
            print('create_terraform_project_file_tags\n', e)
# Downloads the AWS Route53 record
    def download_aws_record(): 
        try:
            if not os.path.exists(os.path.join(dir_path, json_file_name)):
                print('Downloading AWS Route53 record sets. \nZone ID:\t{0} \nName:\t{1}'.format(hosted_zone_id, hosted_zone_name))
                cmd = 'aws route53 list-resource-record-sets --hosted-zone-id {0} > {1} --profile {2}'.format(hosted_zone_id, os.path.join(dir_path, json_file_name), login_profile)      
                os.system(cmd)
        except Exception as e:
            print('download_aws_record\n', e)
# Creates a function name 
    def convert_function_name(self, function_name): 
        try:
            # This function removes numbers and special characters from the start of the record name
            # because import won't run if a function has a special character or number at the start.
            # example: 123abc_property or _123abc_property --> abc_property
            # Alters the name to follow a naming convention 
            # example: abc.defg-property --> abc_defg_property
            function_name = function_name.replace('-', '_')
            function_name = function_name.replace('.', '_')
            function_name = function_name.replace('__', '_')
            # If there's an asterisk in the name
            if r'\052' in function_name:
                function_name = function_name.replace(r'\052', 'asterisk') # Changes * to asterisks_
            
            # If $ and { and } are in the name
            if r'\044' and r'\173' and r'\175' in function_name:
                function_name = function_name.replace(r'\044', '') # Removes $ from name
                function_name = function_name.replace(r'\173', '') # Removes {$} from name
                function_name = function_name.replace(r'\175', '') # Removes } from name
            # If the first character is not an alphanumeric or is a digit it will remove it
            if not function_name[0].isalnum() or function_name[0].isdigit(): 
                for c in function_name:
                    if not function_name[0].isalnum() or function_name[0].isdigit():
                        function_name = function_name.lstrip(function_name[0])
            return function_name
        except Exception as e:
            print('convert_function_name\n', e)
# Converst codoe to special characters
    def convert_mapping_name(self, mapping_name): 
        try:
            # If there's an asterisk in the name
            if r'\052' in mapping_name:
                mapping_name = mapping_name.replace(r'\052', r'*') # Replace code with the symbol
            
            # If $ and { and } are in the name
            if r'\044' and r'\173' and r'\175' in mapping_name:
                mapping_name = mapping_name.replace(r'\044', r'\$') # Replace code with the symbol
                mapping_name = mapping_name.replace(r'\173', r'\{') # Replace code with the symbol
                mapping_name = mapping_name.replace(r'\175', r'\}') # Replace code with the symbol
            return mapping_name
        except Exception as e:
            print('convert_mapping_name\n', e)
# Creates the name that will appear in the record
    def convert_record_name(self, record_name): 
        try:          
            # If there's an asterisk in the name
            if r'\052' in record_name:
                record_name = record_name.replace(r'\052', r'*')  # Replace code with the symbol and the escape backslash so it can be placed in the string
            
            # If $ and { and } are in the name
            if r'\044' and r'\173' and r'\175' in record_name:
                record_name = record_name.replace(r'\044', '\\\$')  # Replace code with the symbol and the escape backslash so it can be placed in the string
                record_name = record_name.replace(r'\173', '\\\{')  # Replace code with the symbol and the escape backslash so it can be placed in the string
                record_name = record_name.replace(r'\175', '}')  # Replace code with the symbol and the escape backslash so it can be placed in the string
            if record_name == hosted_zone_name:
                record_name = 'aws_route53_zone.{0}.name'.format(hosted_zone_function)
            else:
                # Some record names have the property name twice in it
                # example abcd.property.com.property.com
                
                if record_name.count(hosted_zone_name) > 1:
                    hosted_zone_name_count = 0
                    # hozed_zone_name should be removed from record_name, check if there are characters after it and then rebuild accordingly
                    # Currently outputting 'None' because of an error with format and a '{ in field name'
                    while hosted_zone_name_count < record_name.count(hosted_zone_name):
                        if record_name[record_name.find(hosted_zone_name)].isalnum()+1:
                            tmp = record_name[:record_name.find(hosted_zone_name)+len(hosted_zone_name)+record_name.find('.')]
                            record_name = record_name[record_name.find(tmp)+len(tmp):]
                            record_name = record_name.replace(hosted_zone_name, '${{aws_route53_zone.{0}.name}}').format(hosted_zone_function)
                            record_name = tmp + record_name
                        else:
                            record_name = record_name.replace(hosted_zone_name, '${{aws_route53_zone.{0}.name}}').format(hosted_zone_function)
                            record_name = '"' + record_name + '"'
                        hosted_zone_name_count = hosted_zone_name_count + 1
                
                # <prefix>. will be added to property name
                # example logos.origin.property.com
                else:
                    record_name = '"{0}${{aws_route53_zone.{1}.name}}"'.format(record_name[:record_name.find(hosted_zone_name)], hosted_zone_function)    
            return record_name
        except Exception as e:
            print('convert_record_name\n', e, '\nManual change in file required', record_name)
# Record values may have multiple entries
    def convert_route_value(self, value): 
        try:
            # Strips unneccessary values        
            value = value.replace("[{'Value': '", '')
            value = value.replace('''[{'Value': '"''', '')
            value = value.replace("'}]", '')
            value = value.replace(''' ""'}]''', '')
            # These will add a new line between entries
            value = value.replace('''"'}, {'Value': '"''', '", \n"')
            value = value.replace("'}, {'Value': '", '", \n"')
            if value[0] == '"' and value[-1] == '"' and value[-2] == '"':
                value = value.lstrip('"').strip() # Remove " from the start of the string. # .strip() removes whites spaces at both ends of the string.
                value = value.replace('" ""', r'\" \"')
            
            if value[0] == '"' and value[-1] == '"':
                value = value.lstrip('"')
                value = value[:-1]
            return value
        except Exception as e:
            print('convert_route_value\n', e)
# Converts set_Identifers  to following naming converstion
    def convert_set_identifier(self, set_identifer):
        try:
            set_identifer = set_identifer.replace('-', '_')
            set_identifer = set_identifer.replace('.', '_')
            set_identifer = set_identifer.replace('__', '_')
            return set_identifer
        except Exception as e:
            print('convert_set_identifier\n', e)
# Reads from JSON file and assigns varaibles for the write_terraform_file_records() & write_import_script() functions
    def import_json_file_data(): 
            try:
                with open(os.path.join(dir_path, json_file_name)) as json_file: # opens dataframe stream from json file
                    json_data = json.load(json_file) # loads json data
                    count = 0 # loop counter
                    # json data in imported as a dictionary 
                    # ResourceRecordSets is the key and the rest is seen as the value
                    # for each iteration of the while loop variables will be set using the .get() function
                    # example Name": "property.com.", .get('Name') will return property.com.
                    while count < len(json_data['ResourceRecordSets']):
                        original_record_name =  str(json_data['ResourceRecordSets'][count].get('Name')[:-1])
                        function_name= Route53Import().convert_function_name(original_record_name)
                        mapping_name = Route53Import().convert_mapping_name(original_record_name)                        
                        record_name = Route53Import().convert_record_name(original_record_name)                                        
                        multi_value_answer = str(json_data['ResourceRecordSets'][count].get('MultiValueAnswer'))
                        set_identifer = json_data['ResourceRecordSets'][count].get('SetIdentifier')
                        type = str(json_data['ResourceRecordSets'][count].get('Type'))                                    
                        ttl = str(json_data['ResourceRecordSets'][count].get('TTL'))
                        weight = str(json_data['ResourceRecordSets'][count].get('Weight'))
                        # route_to may contain multiple values
                        route_to = Route53Import().convert_route_value(str(json_data['ResourceRecordSets'][count].get('ResourceRecords')))
                        # alias_targets is made up of three varaibles
                        # to assign each value the .find() function is added to the string
                        # zone_id is the value between {'HostedZoneId': ' and ', '
                        # the +len({'HostedZoneId': ') is used to remove the unneccessary value
                        alias_targets = str(json_data['ResourceRecordSets'][count].get('AliasTarget'))
                        dns_name = alias_targets[alias_targets.find("'DNSName': '")+len("'DNSName': '"):alias_targets.find("', 'EvaluateTargetHealth':")]
                        evaluate_target_health = alias_targets[alias_targets.find("'EvaluateTargetHealth': ")+len("'EvaluateTargetHealth': "):alias_targets.find('}')].lower()         
                        zone_id = alias_targets[alias_targets.find("{'HostedZoneId': '")+len("{'HostedZoneId': '"):alias_targets.find("', '")]
                        
                        # Writes the import script file
                        Route53Import.write_import_script(function_name, mapping_name, set_identifer, type)
                        # Writes to the terraform file for this hosted zone
                        Route53Import.write_terraform_file_records(alias_targets, dns_name, evaluate_target_health, function_name, multi_value_answer, \
                                                                   record_name, route_to, set_identifer, ttl, type, weight, zone_id)
                        count = count + 1
            except Exception as e:
                print('import_json_file_data\n', e)
# Function that will create and writes terraform records/functions 
    def write_terraform_file_records(alias_targets, dns_name, evaluate_target_health, function_name, multi_value_answer, 
                                     record_name, route_to, set_identifer, ttl, type, weight, zone_id): 
        try:
            # This is deal with any duplicate naming conflicts
            if set_identifer != 'None':
                function_name = function_name + '_' + Route53Import().convert_set_identifier(str(set_identifer))
            
            if not os.path.exists(os.path.join(dir_path, terraform_file_name)):
                terraform_file = open(os.path.join(dir_path, terraform_file_name), 'a') # Creates terrform file records will be written to and opens dataframe stream to file
                terraform_file.write(
                '''resource "aws_route53_zone" "{0}" {{ \
                \n\tname     = "{1}" \
                \n\tcomment  = "Terraformed: {1}" \
                \n\ttags     = {{}} \
                \n\ttags_all = {{}} \
                \n}}
                '''.format(hosted_zone_function, hosted_zone_name))       
            elif os.path.exists(os.path.join(dir_path, terraform_file_name)):
                # Creates terrform file records will be written to and opens dataframe stream to file
                terraform_file = open(os.path.join(dir_path, terraform_file_name), 'a') 
                function_name = function_name + '_' + type.lower()
                if alias_targets != 'None': # If alias targeting is used
                    record = '''\nresource "aws_route53_record" "{0}" {{ \
                    \n\tzone_id    =    aws_route53_zone.{1}.id \
                    \n\ttype    =    "{2}" \
                    \n\tname    =    {3} \
                    \n\talias {{ \
                    \n\t\tevaluate_target_health    =    {4} \
                    \n\t\tname    =    "{5}" \
                    \n\t\tzone_id    =    "{6}" \
                    \n\t}} \
                    \n}}
                    '''.format(function_name, hosted_zone_function, type, record_name, evaluate_target_health, dns_name, zone_id)
            
                elif weight != 'None': # If weighted routing is uesed
                    record ='''\nresource "aws_route53_record" "{0}" {{  \
                    \n\tzone_id    =    aws_route53_zone.{1}.id \
                    \n\ttype    =    "{2}" \
                    \n\tname    =    {3} \
                    \n\tset_identifier    =    "{4}" \
                    \n\tweighted_routing_policy {{
                    \n\t\tweight    =    "{5}" \
                    \n\t}}             
                    \n\trecords    =    [ \
                    \n\t\t"{6}" \
                    \n\t] \
                    \n\tttl    =    {7} \
                    \n}} 
                    '''.format(function_name, hosted_zone_function, type, record_name, set_identifer, weight, route_to, ttl)
                
                elif multi_value_answer != 'None': # If multi value routing is used
                    record ='''\nresource "aws_route53_record" "{0}" {{  \
                    \n\tzone_id    =    aws_route53_zone.{1}.id \
                    \n\ttype    =    "{2}" \
                    \n\tname    =    {3} \
                    \n\tset_identifier    =    "{4}" \
                    \n\tmultivalue_answer_routing_policy    =  {5} \
                    \n\trecords    =    [ \
                    \n\t\t"{6}" \
                    \n\t] \
                    \n\tttl    =    {7} \
                    \n}} 
                    '''.format(function_name, hosted_zone_function, type, record_name, set_identifer, multi_value_answer.lower(), route_to, ttl)
            
                else: # If standard routing is ued
                    record ='''\nresource "aws_route53_record" "{0}" {{  \
                    \n\tzone_id    =    aws_route53_zone.{1}.id \
                    \n\ttype    =    "{2}" \
                    \n\tname    =    {3} \
                    \n\trecords    =    [ \
                    \n\t\t"{4}" \
                    \n\t] \
                    \n\tttl    =    {5} \
                    \n}} 
                    '''.format(function_name, hosted_zone_function, type, record_name, route_to, ttl)
                terraform_file.write(record)
            
            # Closes data frame stream from and to files
            terraform_file.close()
        except Exception as e:
            print('write_terraform_file_records\n', e)
# Function will create and write a bash file that will contain the terraform import commands
    def write_import_script(function_name, mapping_name, set_identifer, type): 
        try:
            # fucntions_name_ + type.lower() --> property_com_a
            function_name = function_name + '_' + type.lower()
            
            # zome_id + _ + name + type --> ABCDEF_property.com_A_001
            if set_identifer != 'None':
                mapping = hosted_zone_id + '_' + mapping_name +  '_' + type + '_' + Route53Import().convert_set_identifier(str(set_identifer))
            else:
                # zome_id + _ + name + type --> ABCDEF_property.com_A
                mapping = hosted_zone_id + '_' + mapping_name +  '_' + type
            if not os.path.exists(os.path.join(dir_path, terraform_import_file_name)):
                terraform_import_file = open(os.path.join(dir_path, terraform_import_file_name), 'w') # Creates bash file the terrafrom commands will be written to and opens dataframe stream to file 
                terraform_import_file.write('''terraform fmt\nterraform init\nterraform import aws_route53_zone.{0} {1}\n'''.format(hosted_zone_function, hosted_zone_id))
            elif os.path.exists(os.path.join(dir_path, terraform_import_file_name)):
                terraform_import_file = open(os.path.join(dir_path, terraform_import_file_name), 'a')   
                terraform_import_file.write('terraform import aws_route53_record.{0} {1}\n'.format(function_name, mapping))   
            
            # closes data frame stream from and to files
            terraform_import_file.close()
        except Exception as e:
            print('write_import_script\n', e)
Route53Import.create_terraform_project_structure()
Route53Import.download_aws_record() # AWS has a limit as to how many times this API can be called. Once reached your conneciton will be throttled
Route53Import.import_json_file_data()