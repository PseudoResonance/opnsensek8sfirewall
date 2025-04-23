from typing import TypedDict


class RawPort(TypedDict):
    type: str
    port: int
    processData: dict | None


class RawNodeState(TypedDict):
    hostname: str
    ports: list[RawPort]


class RawState(TypedDict):
    searchDomain: str
    nodes: list[RawNodeState]


class Port(TypedDict):
    type: str
    ports: set[int]
    processData: dict


class NodeState(TypedDict):
    hostname: str
    hostnameSimple: str
    fqdn: str
    ports: list[Port]
    processData: dict


def process_raw_state(
    state: RawState,
    verbose=False,
) -> list[NodeState]:
    finalTarget: list[NodeState] = []
    for node in state["nodes"]:
        hostnameSimple = node["hostname"].replace("-", "_").replace(".", "_")
        fqdn = f"{node['hostname']}.{state['searchDomain']}"
        ports: list[Port] = []
        added_port_types: set[str] = set()
        for port in node["ports"]:
            if port["type"] in added_port_types:
                for portType in ports:
                    if portType["type"] == port["type"]:
                        portType["ports"].add(str(port["port"]))
                        break
            else:
                added_port_types.add(port["type"])
                ports.append(
                    {
                        "type": port["type"],
                        "ports": set([str(port["port"])]),
                        "processData": dict(),
                    }
                )
        finalTarget.append(
            {
                "hostname": node["hostname"],
                "hostnameSimple": hostnameSimple,
                "fqdn": fqdn,
                "ports": ports,
                "processData": dict(),
            }
        )
    return finalTarget
