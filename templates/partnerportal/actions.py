from js9 import j

def get_prefab_for_cloudscalers(service):
    node = None

    for parent in service.parents:
        if parent.model.role == 'node':
            node = parent
            break
    ssh_key = node.producers['sshkey'][0]
    key_path = ssh_key.model.data.keyPath
    if not j.sal.fs.exists(key_path):
        raise j.exceptions.RuntimeError("sshkey path not found at %s" % key_path)
    password = node.model.data.sshPassword if node.model.data.sshPassword != '' else None
    passphrase = ssh_key.model.data.keyPassphrase if ssh_key.model.data.keyPassphrase != '' else None
    #executor = j.tools.executor.getSSHBased(addr=node.model.data.ipPublic, port=node.model.data.sshPort,
    #                                        login=node.model.data.sshLogin, passwd=password,
    #                                        allow_agent=True, look_for_keys=True, timeout=5, usecache=False,
    #                                        passphrase=passphrase, key_filename=key_path)

    sshclient = j.clients.ssh.get(addr=node.model.data.ipPublic,
                                  port=node.model.data.sshPort,
                                  login=node.model.data.sshLogin,
                                  passwd=password,
                                  passphrase=passphrase,
                                  allow_agent=True,
                                  look_for_keys=True,
                                  timeout=5,
                                  usecache=False,
                                  key_filename=key_path
                                  )
    executor = j.tools.executor.getFromSSHClient(sshclient=sshclient)

    return j.tools.prefab.get(executor, usecache=False)

def _get_cloud_space(service):

    for parent in service.parents:
        if parent.model.role == 'vdc':
            vdc = parent
            break

    if 'g8client' not in vdc.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue %s" % service)

    g8client = vdc.producers["g8client"][0]
    ovc_client = j.clients.openvcloud.getFromAYSService(g8client)
    ovc_account = ovc_client.account_get(vdc.model.data.account)
    cloudspace = ovc_account.space_get(vdc.model.dbobj.name, vdc.model.data.location)
    return cloudspace

def _get_machine_name(service):
    for parent in service.parents:
        if parent.model.role == 'node':
            node = parent
            break

    return node.name

def _get_node(service):
    for parent in service.parents:
        if parent.model.role == 'node':
            node = parent
            break

    return node

def _add_port_forward(service)
    #import ipdb; ipdb.set_trace()
    cloudspace = _get_cloud_space(service)
    machine_name = _get_machine_name(service)
    machine = cloudspace.machines.get(machine_name)

    unavailable_ports = [int(portinfo['publicPort']) for portinfo in cloudspace.portforwards]
    
    candidate = 8000

    while candidate in unavailable_ports:
        candidate += 1

    available_port = candidate
    
    node = _get_node(service)

    port_forwards = list(node.model.data.ports)
    port_forwards.append("{public}:80".format(public=available_port))
    node.model.data.ports = port_forwards
    node.saveAll()

    try:
        cloudspace.client.api.cloudapi.portforwarding.create(
            cloudspaceId=machine.space.model['id'],
            protocol="tcp",
            localPort=80,
            machineId=machine.model['id'],
            publicIp=machine.space.model['publicipaddress'],
            publicPort=available_port
        )

    except Exception as e:
        raise j.exceptions.RuntimeError("Port forward creation failed for pubic port {} to port 80".format(available_port))

    return available_port

def install(job):
    service = job.service

    # Add port forward
    public_port = _add_port_forward(service)

    # Get prefab for cloudscaler, if not we get prefab for root
    #prefab = get_prefab_for_cloudscalers(service)
    prefab = service.executor.prefab

    try:
        b = prefab.bash
    except Exception as e:
        print("Error while accessing bash")

    data = j.data.serializer.json.loads(service.model.dataJSON)
    env_vars = data.get('vars', [])

    for env_var in env_vars:
        key, value = env_var.split('=',1)
        b.envSet(key, value)
        #prefab.core.run("export {}={}".format(key, value))
        cmd = 'echo "{}={}" >> /etc/environment'.format(key, value)
        prefab.core.run(cmd, profile=True)

    to_dir = '/tmp/pp_setup'
    url = data['url'] 

    prefab.core.dir_ensure(to_dir)

    prefab.core.run("curl {}?$RANDOM > {}/script.sh".format(url, to_dir))

    cmd = """
    cd {to_dir}
    chmod +x script.sh
    ./script.sh
    """.format(to_dir=to_dir)
    
    prefab.core.run(cmd, profile=True)
    ## in the above profile=False ensures that the .bash_profile is sourced before executing the command
    ## needs to be executed by user with sudo rights, w/o password