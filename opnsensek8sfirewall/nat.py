from pyopnsense import firewall
from .state import NodeState


def ensure_nat(
    firewallClient: firewall.FirewallClient,
    categoryUuid: str,
    state: list[NodeState],
    dryRun=False,
    verbose=False,
) -> None:
    rules = firewallClient.get_source_nat([categoryUuid])
    for rule in rules["rows"]:
        if verbose:
            print(f"Checking {rule['description']} NAT rule")
        found = False
        for node in state:
            if node["hostnameSimple"] == rule["description"]:
                found = True
                node["processData"]["natRule"] = rule["uuid"]
                if verbose:
                    print(f"NAT Rule {rule['description']} matches a hostname")
                break
        if not found:
            print(f"Removing NAT rule {rule['description']}")
            if dryRun:
                print(f"Delete source NAT: {rule['uuid']}")
            else:
                result = firewallClient.del_source_nat(rule["uuid"])
                if verbose:
                    print(result)
    for node in state:
        if "natRule" not in node["processData"]:
            print(f"Adding NAT rule {node['hostnameSimple']}")
            if dryRun:
                print(f"Add source NAT: {node['hostnameSimple']}")
            else:
                result = firewallClient.add_source_nat(
                    {
                        "rule": {
                            "enabled": "1",
                            "nonat": "0",
                            "sequence": "1",
                            "interface": "wan",
                            "ipprotocol": "inet",
                            "protocol": "TCP",
                            "source_net": "any",
                            "source_port": "",
                            "destination_net": "__wan_network",
                            "destination_port": "30585",
                            "target": node["hostnameSimple"],
                            "target_port": "",
                            "log": "0",
                            "categories": categoryUuid,
                            "description": node["hostnameSimple"],
                        }
                    }
                )
                node["processData"]["natRule"] = result["uuid"]
                if verbose:
                    print(result)
