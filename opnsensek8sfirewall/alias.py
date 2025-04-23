from typing import TypedDict
from pyopnsense import firewall
from .state import NodeState


class Alias(TypedDict):
    name: str
    uuid: str


def ensure_aliases(
    firewallClient: firewall.FirewallClient,
    categoryUuid: str,
    state: list[NodeState],
    dryRun=False,
    verbose=False,
) -> list[Alias]:
    aliases = firewallClient.get_aliases(
        searchType=["host"], searchCategories=[categoryUuid]
    )
    old_aliases: list[Alias] = []
    for alias in aliases["rows"]:
        if verbose:
            print(f"Checking {alias['name']} alias")
        found = False
        for node in state:
            if node["hostnameSimple"] == alias["name"]:
                found = True
                node["processData"]["alias"] = alias["uuid"]
                if verbose:
                    print(f"Alias {alias['name']} matches a hostname")
                if alias["content"] != node["fqdn"]:
                    print(f"Updating alias {alias['name']} FQDN")
                    if dryRun:
                        print(
                            f"Set alias: {alias['uuid']} host: {node['fqdn']}")
                    else:
                        result = firewallClient.set_alias(
                            alias["uuid"],
                            {
                                "alias": {
                                    "content": node["fqdn"],
                                },
                                "network_content": "",
                                "authgroup_content": "",
                            },
                        )
                        if verbose:
                            print(result)
                break
        if not found:
            print(f"Marking alias {alias['name']} for removal")
            old_aliases.append({"name": alias["name"], "uuid": alias["uuid"]})
    for node in state:
        if "alias" not in node["processData"]:
            print(f"Adding alias {node['hostnameSimple']}")
            if dryRun:
                print(f"Add alias with host: {node['fqdn']}")
            else:
                result = firewallClient.add_alias(
                    {
                        "alias": {
                            "enabled": "1",
                            "name": node["hostnameSimple"],
                            "type": "host",
                            "categories": categoryUuid,
                            "content": node["fqdn"],
                            "counters": "0",  # Statistics
                            "description": "Managed by OPNSense K8s Firewall",
                        },
                        "network_content": "",
                        "authgroup_content": "",
                    }
                )
                node["processData"]["alias"] = result["uuid"]
                if verbose:
                    print(result)
    return old_aliases


def ensure_port_aliases(
    firewallClient: firewall.FirewallClient,
    categoryUuid: str,
    state: list[NodeState],
    dryRun=False,
    verbose=False,
) -> list[Alias]:
    aliases = firewallClient.get_aliases(
        searchType=["port"], searchCategories=[categoryUuid]
    )
    old_aliases: list[Alias] = []
    for alias in aliases["rows"]:
        aliasNameSplit = alias["name"].split("__")
        found = False
        if len(aliasNameSplit) >= 2:
            if verbose:
                print(
                    f'Checking {alias["name"]} port alias for hostname "{aliasNameSplit[0]}" and port type "{aliasNameSplit[1]}"'
                )
            for node in state:
                if node["hostnameSimple"] == aliasNameSplit[0]:
                    for port in node["ports"]:
                        if port["type"] == aliasNameSplit[1]:
                            found = True
                            port["processData"]["alias"] = alias["uuid"]
                            if verbose:
                                print(
                                    f"Port alias {alias['name']} matches a hostname and port type"
                                )
                            aliasPorts = set(alias["content"].split("\n"))
                            difference = len(aliasPorts ^ port["ports"])
                            if difference > 0:
                                print(
                                    f"Updating port alias {alias['name']} port list")
                                if dryRun:
                                    print(
                                        f"Set alias: {alias['uuid']} ports: {','.join(port['ports'])}"
                                    )
                                else:
                                    result = firewallClient.set_alias(
                                        alias["uuid"],
                                        {
                                            "alias": {
                                                "content": f"{'\n'.join(port['ports'])}",
                                            },
                                            "network_content": "",
                                            "authgroup_content": "",
                                        },
                                    )
                                    if verbose:
                                        print(result)
                            break
                if found:
                    break
        if not found:
            print(f"Marking port alias {alias['name']} for removal")
            old_aliases.append({"name": alias["name"], "uuid": alias["uuid"]})
    for node in state:
        for port in node["ports"]:
            if "alias" not in port["processData"]:
                print(
                    f"Adding port alias {node['hostnameSimple']}__{port['type']}")
                if dryRun:
                    print(f"Add alias with ports: {','.join(port['ports'])}")
                else:
                    result = firewallClient.add_alias(
                        {
                            "alias": {
                                "enabled": "1",
                                "name": f"{node['hostnameSimple']}__{port['type']}",
                                "type": "port",
                                "categories": categoryUuid,
                                "content": f"{'\n'.join(port['ports'])}",
                                "counters": "0",  # Statistics
                                "description": "Managed by OPNSense K8s Firewall",
                            },
                            "network_content": "",
                            "authgroup_content": "",
                        }
                    )
                    port["processData"]["alias"] = result["uuid"]
                    if verbose:
                        print(result)
    return old_aliases


def delete_old_aliases(
    firewallClient: firewall.FirewallClient,
    old_aliases: list[Alias],
    dryRun=False,
    verbose=False,
) -> None:
    for alias in old_aliases:
        if verbose:
            print(f"Removing alias {alias['name']}")
        if dryRun:
            print(f"Delete alias: {alias['uuid']}")
        else:
            result = firewallClient.del_alias(alias["uuid"])
            if verbose:
                print(result)
