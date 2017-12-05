# Partner Portal Host

## Tested on the AYS Server of Artilium

- vm-1207 ("AYS-Server"): https://se-gen-1.demo.greenitglobe.com/CBGrid/Virtual%20Machine?id=1207
  - Directories:
    - JumpScale: `/opt/code/github/jumpscale`
    - AYS Repositories: `/opt/var/cockpit_repos/`
    - Configuration: `/opt/cfg/portals/main/config.yaml`
  - SSH: `ssh -A root@195.143.34.162 -p7222`
    - JumpScale Portal configuration: `vim /opt/cfg/portals/main/config.yaml`
  - ItsYou.online: https://itsyou.online/#/organization/artilium-dev2.ays-server-clients/settings
    - Get the JWT, AYS command line tool: `ays generatetoken --client_id root@..." -validity=3600`
    artilium-dev2 » ays-server-clients » ays-portal-users
    - JWT: `ays generatetoken --clientid "artilium-dev2.ays-server-clients" --clientsecret $KEY_SECRET --validity 3600`
  - Portal: http://195.143.34.162:8200



Install capnp:
```bash
apt-get install capnproto
capnp id
```

## On the AYS Server

Create the repository:
```bash
ays generatetoken --clientid "artilium-dev2.ays-server-clients" --clientsecret $KEY_SECRET --validity 3600
ays repo create -n pp -g http://pp
```

Create actor template directory:
```bash
cd pp
mkdir actorTemplates/partnerportal
```

Copy the template:
```bash
scp -P 7222 ~/code/gogs/yves/partnerportal/template/*.* root@195.143.34.162:/opt/var/cockpit_repos/pp/actorTemplates/partnerportal
```



## JWT

For the blueprint:
```python
import os
app_id = os.environ["APP_ID"]
secret = os.environ["SECRET"]
jwt = j.clients.itsyouonline.get_jwt(app_id, secret)
```

For the AYS Server:
```python
import os
app_id = os.environ["APP_ID"]
secret = os.environ["SECRET"]
iyo_user = j.clients.itsyouonline.get_user(app_id, secret)
ays_server_clients_org = iyo_user.organizations.get("artilium-dev2.ays-server-clients")
org_key = ays_server_clients_org.api_keys.get("ays-server-client-secret")
ays_jwt = j.clients.itsyouonline.get_jwt("artilium-dev2.ays-server-clients", org_key.model["secret"]) 
```


