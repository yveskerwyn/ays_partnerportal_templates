# AYS Templates for Partner Portals

- [Add the templates to your AYS Server](#add-templates)
- [How to use the templates](#how-to-use)

<a id="add-templates"></a>
## Add the templates to your AYS Server

Requirements:
- AYS Server 9.2.0 or 9.3.0
- The below example script to add the templates to your AYS Server require a JumpScale 9.3.0 interactive shell
- On ItsYou.online
  - Personal profile for which you created and API access key
    - In the below script requires that you export application ID and secret into environment variables
  - Owner or member access to the ItsYou.online organization that was used to setup the AYS server
    - In the below script this organization is `artilium-dev2.ays-server-clients`
    - The API access key enabled for client credentials flow in the example is label `ays-server-client-secret`

Export your personal application id and secret:
```bash
export APP_ID="..."
export SECRET="..."
```

Execute the following commend from the JumpScale 9.3.0 interactive shell:
```python
import os
app_id = os.environ["APP_ID"]
secret = os.environ["SECRET"]
iyo_user = j.clients.itsyouonline.get_user(app_id, secret)
ays_server_clients_org = iyo_user.organizations.get("artilium-dev2.ays-server-clients")
org_key = ays_server_clients_org.api_keys.get("ays-server-client-secret")
ays = j.clients.ays.get("artilium-dev2.ays-server-clients", org_key.model["secret"], "http://195.143.34.162:5000")
ays.templates.addTemplates("https://github.com/yveskerwyn/ays_partnerportal_templates", "master")
```

<a id="how-to-use"></a>
## How to use the templates

Check the blueprint examples in the [blueprints](/blueprints)

You will have to update the following in the blueprints:
- [jwt](#jwt)
- **url**: url of the targeted OpenvCloud system
- **account**: OpenvCloud account
- **location**: OpenvCloud location name
- **vdc**: AYS service name, in the example blueprints it is `partnerportals`
- **node.ovc**: AYS service name, in the example blueprints it is `pphost`
- **bootdisk.size**: boot disk size of the virtual machine in GB, e.g. 50 GB 
- **memory**: memory of the virtual machine in GB, e.g. 4 GB
- **os.image**: OS image to install on the virtual machine, e.g. "Ubuntu 16.04 x64"; make sure the image is available and enabled on the target system
- [vars](#vars): the list of environment variables you want to pass
- [url](#script-url): url from which your installation script can be downloaded

<a id="jwt"></a>
### JWT

The JSON Web token (JWT) in the blueprint needs to be created for an ItsYou.online user that has been granted access to the target OpenvCloud environment.

Here's how to create the JWT from the JumpScale 9.3.0 interactive shell, using the exported application ID and secret:
```python
import os
app_id = os.environ["APP_ID"]
secret = os.environ["SECRET"]
jwt = j.clients.itsyouonline.get_jwt(app_id, secret)
```

<a id="vars"></a>
### Environment variables 

This is a list of variables that will be exported in the virtual machine, using the following formatting:
```yaml
  vars:
    - '<key>=value'
    - ...
```

> Note that the variables are only exported for the default `cloudscaler` user.

In the example two variables are exported:
```yaml
  vars:
    - 'var1=hello'
    - 'var2=world'
```

<a id="script-url"></a>
### Script url

The script will be downloaded from the specified url and saved in `~/tmp/pp_setup/script.sh`.

> Note that the script is executed for the default `cloudscaler` user.

In the example the [testscript.sh](testscrip.sh) is downloaded form this repository, which will simple read the exported environment variable into an output fil