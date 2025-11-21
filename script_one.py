from zabbix_utils import ZabbixAPI
import os
import requests
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning
from dotenv import load_dotenv


# Disable SSL warnings for insecure requests
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def get_picture(ip, name, user, passwd):
    """Downloads image from IP camera"""
    try:
        url = f'https://{ip}/ISAPI/Streaming/channels/1/picture'
        response = requests.get(url, auth=HTTPDigestAuth(user, passwd), verify=False, timeout=10)
        
        filename = f'{name}.jpg'
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Image downloaded successfully as {filename}")
            return True
        else:
            print(f"Failed to download image for {name}. Status code: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print(f"Timeout error for camera {name} at {ip}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image for {name}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error for {name}: {e}")
        return False


def main():
    """Main program function"""
    load_dotenv()
    
    # Create and navigate to working directory
    path = '.\\data'
    os.makedirs(path, exist_ok=True)
    os.chdir(path)

    # Load environment variables
    zab_ip = os.getenv('ZAB_IP')
    zab_usr = os.getenv('ZAB_USR')
    zab_passwd = os.getenv('ZAB_PASSWD')

    cams_usr = os.getenv('CAMS_USR')
    cams_passwd = os.getenv('CAMS_PASSWD')
    cams_group = os.getenv('CAMS_GROUP')

    # Check for required environment variables
    if not all([zab_ip, zab_usr, zab_passwd, cams_usr, cams_passwd, cams_group]):
        print("Error: Missing required environment variables")
        return

    try:
        # Connect to Zabbix API
        zapi = ZabbixAPI(
            url=f"https://{zab_ip}/api_jsonrpc.php",
            user=zab_usr,
            password=zab_passwd,
            validate_certs=False
        )
        
        print(f"Connected to Zabbix API successfully")
        
        # Get camera group ID
        groups = zapi.hostgroup.get(filter={'name': cams_group}, output=['groupid'])
        
        if not groups:
            print(f"Error: Group '{cams_group}' not found")
            return
            
        group_id = groups[0]['groupid']
        print(f"Found group: {cams_group} (ID: {group_id})")

        # Get hosts from group
        hosts = zapi.host.get(groupids=[group_id], output=['hostid', 'name'])
        print(f"Found {len(hosts)} hosts in group")
        
        # Process each host
        success_count = 0
        for host in hosts:
            print(f"\nProcessing host: {host['name']}")
            macros = zapi.usermacro.get(output=['value'], hostids=host['hostid'])
            
            if not macros:
                print(f"  No macros found for {host['name']}")
                continue
                
            for macro in macros:
                if get_picture(macro['value'], host['name'], cams_usr, cams_passwd):
                    success_count += 1

        print(f"\n{'='*50}")
        print(f"Download completed: {success_count}/{len(hosts)} images successful")
        
        # Logout from Zabbix API
        zapi.logout()
        print("Logged out from Zabbix API")

    except Exception as e:
        print(f"Connection or processing error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
