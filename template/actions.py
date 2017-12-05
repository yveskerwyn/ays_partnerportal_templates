from js9 import j

def get_prefab_for_cloudscaler(service):
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
    executor = j.tools.executor.getSSHBased(addr=node.model.data.ipPublic, port=node.model.data.sshPort,
                                            login=node.model.data.sshLogin, passwd=password,
                                            allow_agent=True, look_for_keys=True, timeout=5, usecache=False,
                                            passphrase=passphrase, key_filename=key_path)

    return j.tools.prefab.get(executor, usecache=False)

def install(job):
    service = job.service

    # Get prefab for cloudscaler, if not we get prefab for root
    prefab = get_prefab_for_cloudscaler(service)
    #prefab = service.executor.prefab

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

    b.envSet("test1", "val1")
    b.envSet("test2", "val2")
    to_dir = '~/tmp/pp_setup'
    url = data['url'] 
    #root_prefab.core.file_download(url, overwrite=True, to=to_dir, expand=False, removeTopDir=False)
    #prefab.core.file_download(url, overwrite=True, to=to_dir, expand=False, removeTopDir=False)
    prefab.core.dir_ensure(to_dir)

    prefab.core.run("curl {}?$RANDOM >> {}/script.sh".format(url, to_dir))

    cmd = """
    cd {to_dir}
    chmod +x script.sh
    ./script.sh
    """.format(to_dir=to_dir)

    prefab.core.run(cmd, profile=True)
    ## in the above profile=False ensures that the .bash_profile is sourced before executing the command
    ## needs to be executed by user with sudo rights, w/o password