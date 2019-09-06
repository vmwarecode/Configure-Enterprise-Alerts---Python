#
# Configure EDGE_UP and EDGE_DOWN alerts on the target enterprise
# 
# Usage: VC_USERNAME='user@velocloud.net' VC_PASSWORD=s3cret python configure_enterprise_alerts.py
#

import os
from datetime import datetime, timedelta
from client import *

# EDIT THESE
VCO_HOSTNAME = 'vcoX.velocloud.net'
ENTERPRISE_ID = 1
ALERT_TYPES = ['EDGE_DOWN','EDGE_UP']
# The complete list of supported alert types may be parsed from the repsonse to a call to the
# `alert/getEnterpriseAlertDefinitions` method

def main():

    client = VcoRequestManager(VCO_HOSTNAME)
    client.authenticate(os.environ['VC_USERNAME'], os.environ['VC_PASSWORD'], is_operator=os.environ.get('VC_OPERATOR', False))

    definitions = client.call_api('alert/getEnterpriseAlertDefinitions', {
        'enterpriseId': ENTERPRISE_ID
    })

    configurations = client.call_api('enterprise/getEnterpriseAlertConfigurations', {
        'enterpriseId': ENTERPRISE_ID
    })

    for target_type in ALERT_TYPES:

        # Check whether these alerts already exist
        configuration_exists = False
        for configuration in configurations:
            if configuration['name'] == target_type:
                configuration_exists = True
                print 'Alert configuration of type %s already exists - enabling...' % target_type
                configuration['enabled'] = 1
                break

        if not configuration_exists:
            target_definition = [d for d in definitions if d['name'] == target_type][0]
            configurations.append(make_alert_configuration(target_definition))

    print 'Updating alert configurations...'
    client.call_api('enterprise/insertOrUpdateEnterpriseAlertConfigurations', {
        'enterpriseId': ENTERPRISE_ID,
        'enterpriseAlertConfigurations': configurations
    })
    print 'Success!'

"""
Generate an alert configuration, given a definition
"""
def make_alert_configuration(definition):
    ret = { k: definition[k] for k in ['name','type','description','definition','firstNotificationSeconds','maxNotifications','notificationIntervalSeconds','resetIntervalSeconds']}
    ret['alertDefinitionId'] = definition['id']
    ret['enterpriseId'] = ENTERPRISE_ID
    ret['enabled'] = 1
    return ret

if __name__ == '__main__':
    main()
