from ApiMangerConfigUtil.unzippingAPIMs import unzipFiles
from ApiMangerConfigUtil.run_APIM import runAPIM
from ApiMangerConfigUtil.stop_running_APIM import stopRunningServer
from ApiMangerConfigUtil.configuring_synapse_and_tenants import *
from ApiMangerConfigUtil.run_gateway_artifacts_config_script import runGatewayArtifacts
from ApiMangerConfigUtil.configuring_identity_components import *
from ApiMangerConfigUtil.remove_files import *
from ApiMangerConfigUtil.change_config_files import *
from ApiMangerConfigUtil.waiting import wait
from ApiMangerConfigUtil.run_jmeter_scripts import runJmeter
from ApiMangerConfigUtil.xml_file_change import *
from ApiMangerConfigUtil.tier_down import tier_down
from DbUtil.copy_db_connector import copyDbConnector
from DbUtil.run_sql_queries import *
import re

def main():
    # Unzipping all the given API Manager versions
    unzipFiles()

    # Copy database connector into repository/compone   nts/lib directory
    copyDbConnector(APIM_HOME_PATH, OLD_VERSION)

    # Create tables in provided database information
    createTables()

    if (re.match("[3].[0-9].[0-9]", OLD_VERSION)):
        conf_deployment_toml(OLD_VERSION)
        change_file("deployment.toml file", '../data/API-M_%s/deployment.toml' % OLD_VERSION,
                    '%s/wso2am-%s/repository/conf/deployment.toml' % (APIM_HOME_PATH, OLD_VERSION))
    else:
        # Do required configurations according to the given database type and credentials
        conf_master_datasource()

        # master-datasource.xml file changing
        if DB_TYPE == 'mysql':

            change_file("master-datasources.xml file", '../data/dbconnectors/mysql/master-datasources.xml',
                    '%s/wso2am-%s/repository/conf/datasources/master-datasources.xml' % (APIM_HOME_PATH, OLD_VERSION))

        elif DB_TYPE == 'oracle':

            change_file("master-datasources.xml file", '../data/dbconnectors/oracle/master-datasources.xml',
                    '%s/wso2am-%s/repository/conf/datasources/master-datasources.xml' % (APIM_HOME_PATH, OLD_VERSION))

        elif DB_TYPE == 'mssql':

            change_file("master-datasources.xml file", '../data/dbconnectors/mssql/master-datasources.xml',
                        '%s/wso2am-%s/repository/conf/datasources/master-datasources.xml' %
                        (APIM_HOME_PATH, OLD_VERSION))

        elif DB_TYPE == 'postgresql':

            change_file("master-datasources.xml file", '../data/dbconnectors/postgresql/master-datasources.xml',
                           '%s/wso2am-%s/repository/conf/datasources/master-datasources.xml' %
                        (APIM_HOME_PATH, OLD_VERSION))
        else:
            print("Database type provided is not valid when configuring master-datasource xml file!!!")

        # registry.xml file changing
        if re.match("[2].[0-6].[0-9]", OLD_VERSION) and re.match("[3].[0-9].[0-9]", NEW_VERSION):
            change_file("registry.xml file", '../data/API-M_%s/version_disabled/registry.xml' % OLD_VERSION,
               '%s/wso2am-%s/repository/conf/registry.xml' % (APIM_HOME_PATH, OLD_VERSION))
            disable_registry_version()
        else:
            change_file("registry.xml file", '../data/API-M_%s/registry.xml' % OLD_VERSION,
               '%s/wso2am-%s/repository/conf/registry.xml' % (APIM_HOME_PATH, OLD_VERSION))

        # user-mgt.xml file changing
        change_file("user-mgt.xml", '../data/user-mgt.xml',
                  '%s/wso2am-%s/repository/conf/user-mgt.xml' % (APIM_HOME_PATH, OLD_VERSION))

        # Enabling JWT in api-manager.xml
        # --This is for testing of jwt token in testing

        # --Uncomment the jwt enabling phrase
        uncomment_xml('%s/wso2am-%s/repository/conf/api-manager.xml' % (APIM_HOME_PATH, OLD_VERSION),
                      "EnableJWTGeneration")

        # --Change value of <EnableJWTGeneration> to true
        edit_xml('%s/wso2am-%s/repository/conf/api-manager.xml' % (APIM_HOME_PATH, OLD_VERSION),
                 "<EnableJWTGeneration>", "\t<EnableJWTGeneration>true</EnableJWTGeneration> \n")

        # --Change value of <JWTHeader> to jwt to use in testing process
        edit_xml('%s/wso2am-%s/repository/conf/api-manager.xml' % (APIM_HOME_PATH, OLD_VERSION), "<JWTHeader>",
               "\t<JWTHeader>jwt</JWTHeader> \n")

    # Copy backEndService.xml for testing purposes
    # --This back end service will forward all the requests same as it received
    # --For token validation
    change_file("backEndService.xml file", '../data/backEndService.xml',
                    '%s/wso2am-%s/repository/deployment/server/synapse-configs/default/api/backEndService.xml'
                    % (APIM_HOME_PATH, OLD_VERSION))

    # run old API Manger version with database connection
    runAPIM(APIM_HOME_PATH, OLD_VERSION)
    #
    # # Waiting till server getting started
    wait()
    #
    # # Run users and roles creation JMeter script on running APIM
    runJmeter("RolesAndUsersCreation")

    # Run data population script to generate some previously used data on running old version of APIM
    if (re.match("[3].[0-9].[0-9]", OLD_VERSION)):
        runJmeter("latest_DataPopulationInOldVersion")
    else:
        runJmeter("DataPopulationInOldVersion")

    # Stop running old version of API Manager
    stopRunningServer(APIM_HOME_PATH, OLD_VERSION)

    check = input("Are you ready to continue for migration([y]/[n]): ")
    if check.strip().lower() == "y":

        # ***************************Configurations in new APIM***************************************

        # Copy database connector into repository/components/lib directory
        copyDbConnector(APIM_HOME_PATH, NEW_VERSION)

        if (re.match("[3].[0-9].[0-9]", NEW_VERSION)):
            conf_deployment_toml(NEW_VERSION)
            change_file("deployment.toml file", '../data/API-M_%s/deployment.toml' % NEW_VERSION,
                    '%s/wso2am-%s/repository/conf/deployment.toml' % (APIM_HOME_PATH, NEW_VERSION))

        else :
        # master-datasource.xml file changing
            if DB_TYPE == 'mysql':

                change_file("master-datasources.xml file", '../data/dbconnectors/mysql/master-datasources.xml',
                        '%s/wso2am-%s/repository/conf/datasources/master-datasources.xml' %
                        (APIM_HOME_PATH, NEW_VERSION))

            elif DB_TYPE == 'oracle':

                change_file("master-datasources.xml file", '../data/dbconnectors/oracle/master-datasources.xml',
                        '%s/wso2am-%s/repository/conf/datasources/master-datasources.xml' %
                        (APIM_HOME_PATH, NEW_VERSION))

            elif DB_TYPE == 'mssql':

                change_file("master-datasources.xml file", '../data/dbconnectors/mssql/master-datasources.xml',
                        '%s/wso2am-%s/repository/conf/datasources/master-datasources.xml' %
                        (APIM_HOME_PATH, NEW_VERSION))

            elif DB_TYPE == 'postgresql':

                change_file("master-datasources.xml file", '../data/dbconnectors/postgresql/master-datasources.xml',
                        '%s/wso2am-%s/repository/conf/datasources/master-datasources.xml' %
                        (APIM_HOME_PATH, NEW_VERSION))

            else:
                print("Database type provided is not valid when configuring master-datasource xml file!!!")

            # registry.xml file changing
            change_file("registry.xml file", '../data/API-M_%s/registry.xml' % NEW_VERSION,
                    '%s/wso2am-%s/repository/conf/registry.xml' % (APIM_HOME_PATH, NEW_VERSION))

            # user-mgt.xml file changing
            change_file("user-mgt.xml", '../data/user-mgt.xml',
                    '%s/wso2am-%s/repository/conf/user-mgt.xml' % (APIM_HOME_PATH, NEW_VERSION))

        # Moving all the mentioned configuaration files in migration document from old API Manger to new
        # --Moving synapse files
        moveSynapse()
        # # --Copying tenants
        copyTenants()
        #
        # # Running gate way artifacts script in new API Manager version
        if not (OLD_VERSION == "2.5.0" and NEW_VERSION == "2.6.0"):
            runGatewayArtifacts()
        #
        # # Upgrading databases as mentioned in migration documentation
        upgradeDBs()
        #
        # # Identity componants configuring
        upgrade_identity_components()

        check = input("Are you ready to continue([y]/[n]): ")
        if check.strip().lower() == "y":

            # Copy access control migration clint and remove previously copied org.wso2.carbon.is.migration-5.6.0.jar jar file and migration-resources zip file generated
             if not (OLD_VERSION == "2.2.0" and NEW_VERSION == "2.5.0") and not (OLD_VERSION == "2.5.0"
                 and NEW_VERSION == "2.6.0") and not (OLD_VERSION == "2.2.0" and NEW_VERSION == "2.6.0"):
                 access_control_migration_client()

             check = input("Are you ready to continue([y]/[n]): ")
             if check.strip().lower() == "y":
                 if OLD_VERSION == "2.0.0":
                     print("Please manually go and add property under AuthorizationManager in user-mgt.xml mentioned in wso2 migration doc")
                     check = input("Are you ready to continue([y]/[n]): ")
                     if check.strip().lower() == "y":
                         print("Thank you for your cooperation!")

                 # Upgrade registry database with new configurations of tables
                 confRegDB()
                 # Copy tenant loader jar
                 copy_tenant_loader("../data/re_indexing_registry/tenantloader-1.0.jar",
                                   '%s/wso2am-%s/repository/components/dropins' % (APIM_HOME_PATH, NEW_VERSION))

                 if (re.match("[3].[0-9].[0-9]", NEW_VERSION)):
                    # re-indexing artifacts
                    edit_toml('%s/wso2am-%s/repository/conf/deployment.toml' % (APIM_HOME_PATH, NEW_VERSION),
                              "re_indexing= 1", "re_indexing= 2")
                    reindex_artifacts()
                 else:
                    reindex_artifacts2('%s/wso2am-%s/repository/conf/registry.xml' % (APIM_HOME_PATH, NEW_VERSION))
                                      # run old API Manger version with database connection
                 runAPIM(APIM_HOME_PATH, NEW_VERSION)

                 print("Please manually check and stop(^c) the APIM server after it get started...")
                 wait()

                 check = input("Are you ready to continue([y]/[n]): ")
                 if check.strip().lower() == "y":
                      # Remove copied tenant loader jar file
                      remove_tenant_loaderJar()
                      # Remove client migration zip file
                      remove_client_migration_zip()

                      #Enabling JWT in api-manager.xml
                      # --This is for testing of jwt token in testing
                      if not (re.match("[3].[0-9].[0-9]", NEW_VERSION)):
                        # --Uncomment the jwt enabling phrase
                        uncomment_xml('%s/wso2am-%s/repository/conf/api-manager.xml' % (APIM_HOME_PATH, NEW_VERSION),
                                  "EnableJWTGeneration")

                        # --Change value of <EnableJWTGeneration> to true
                        edit_xml('%s/wso2am-%s/repository/conf/api-manager.xml' % (APIM_HOME_PATH, NEW_VERSION),
                             "<EnableJWTGeneration>",
                             "\t<EnableJWTGeneration>true</EnableJWTGeneration> \n")

                        # --Change value of <JWTHeader> to jwt to use in testing process
                        edit_xml('%s/wso2am-%s/repository/conf/api-manager.xml' % (APIM_HOME_PATH, NEW_VERSION), "<JWTHeader>",
                             "\t<JWTHeader>jwt</JWTHeader> \n")

                      runAPIM(APIM_HOME_PATH, NEW_VERSION)

                      wait()

                      # test previous version's data using JMeter script on running new APIM
                      if (re.match("[3].[0-9].[0-9]", NEW_VERSION)):
                        runJmeter("latest_Validation_in_new_APIM")
                      else:
                        runJmeter("Validation_in_new_APIM")

                      # Integration testing using JMeter script on running new APIM
                      if (re.match("[3].[0-9].[0-9]", NEW_VERSION)):
                          runJmeter("latest_Integration_testing_in_new_APIM")
                      else:
                          runJmeter("Integration_testing_in_new_APIM")

if __name__ == "__main__":
    main()
