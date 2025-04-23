from pyopnsense import firewall
from .state import NodeState


def ensure_filter(
    firewallClient: firewall.FirewallClient,
    categoryUuid: str,
    state: list[NodeState],
    dryRun=False,
    verbose=False,
) -> None:
    rules = firewallClient.get_filter_rule([categoryUuid])
    for rule in rules["rows"]:
        ruleNameSplit = rule["description"].split("__")
        found = False
        if len(ruleNameSplit) >= 2:
            if verbose:
                print(
                    f'Checking {rule["description"]} filter rule for hostname "{ruleNameSplit[0]}" and port type "{ruleNameSplit[1]}"'
                )
            for node in state:
                if node["hostnameSimple"] == ruleNameSplit[0]:
                    for port in node["ports"]:
                        if port["type"] == ruleNameSplit[1]:
                            found = True
                            port["processData"]["filterRule"] = rule["uuid"]
                            if verbose:
                                print(
                                    f"Filter rule {rule['description']} matches a hostname and port type"
                                )
                            break
        if not found:
            print(f"Removing filter rule {rule['description']}")
            if dryRun:
                print(f"Delete filter rule: {rule['uuid']}")
            else:
                result = firewallClient.del_filter_rule(rule["uuid"])
                if verbose:
                    print(result)
    for node in state:
        for port in node["ports"]:
            if "filterRule" not in port["processData"]:
                print(
                    f"Adding filter rule {node['hostnameSimple']}__{port['type']}")
                if dryRun:
                    print(
                        f"Add filter rule: {node['hostnameSimple']}__{port['type']} port: {port['type']}"
                    )
                else:
                    result = firewallClient.add_filter_rule(
                        {
                            "rule": {
                                "sequence": "1",
                                "categories": categoryUuid,
                                "description": f"{node['hostnameSimple']}__{port['type']}",
                                "enabled": "1",
                                "action": "pass",
                                "interface": "wan",
                                "protocol": port["type"],
                                "source_net": "any",
                                "source_port": "",
                                "destination_net": "wanip",
                                "destination_port": f"{node['hostnameSimple']}__{port['type']}",
                                "log": "0",
                            }
                        }
                    )
                    node["processData"]["filterRule"] = result["uuid"]
                    if verbose:
                        print(result)
