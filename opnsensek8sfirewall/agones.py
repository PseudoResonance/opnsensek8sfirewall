import time
from typing import Callable
from kubernetes_asyncio import client, watch
from .state import RawState

GROUP = "agones.dev"
VERSION = "v1"
PLURAL = "gameservers"


def process_resource(state: RawState, resource, verbose=False) -> None:
    stateNode = None
    if "nodeName" not in resource["status"] or len(resource["status"]["nodeName"]) == 0:
        print(
            f"Resource {resource["metadata"]["name"]} in namespace {resource["metadata"]["namespace"]} not yet assigned to a node!")
        return
    for node in state["nodes"]:
        if node["hostname"] == resource["status"]["nodeName"]:
            stateNode = node
            break
    if stateNode is None:
        stateNode = {
            "hostname": resource["status"]["nodeName"], "ports": []}
        state["nodes"].append(stateNode)
    print(
        f"Discovered {resource["metadata"]["name"]} in namespace {resource["metadata"]["namespace"]} on node {resource["status"]["nodeName"]}")
    containerName = None
    if "container" in resource["spec"]:
        containerName = resource["spec"]["container"]
    for port in resource["spec"]["ports"]:
        if containerName is not None and port["container"] != containerName:
            continue
        if "hostPort" in port:
            stateNode["ports"].append(
                {"type": port["protocol"], "port": str(port["hostPort"]), "processData": {"uid": resource["metadata"]["uid"]}})
            if verbose:
                print(f"Found {port["protocol"]} port {port["hostPort"]}")
        else:
            print(
                f"Port {port["name"] if "name" in port else "UNKNOWN"} ({port["containerPort"]}) {resource["metadata"]["name"]} is missing a host port!")


def delete_resource(state: RawState, resource, verbose=False) -> None:
    for node in state["nodes"]:
        if node["hostname"] == resource["status"]["nodeName"]:
            print(
                f"Removing {resource["metadata"]["name"]} in namespace {resource["metadata"]["namespace"]} on node {resource["status"]["nodeName"]}")
            for port in node["ports"][:]:
                if "processData" in port and "uid" in port["processData"] and port["processData"]["uid"] == resource["metadata"]["uid"]:
                    node["ports"].remove(port)
                    if verbose:
                        print(
                            f"Removing {port["type"]} port {port["port"]}")
            return


async def watch_resources(setApplicationState: Callable[[bool], None], reconcileCallback: Callable[[RawState], None], searchDomain: str = "", searchNamespace: str = "", verbose=False) -> None:
    state: RawState = {"nodes": [], "searchDomain": searchDomain}
    print("Fetching current resources...")
    api = client.CustomObjectsApi()
    objects = await api.list_namespaced_custom_object(
        group=GROUP,
        version=VERSION,
        namespace=searchNamespace,
        plural=PLURAL
    )
    resourceVersion = objects["metadata"]["resourceVersion"]
    if verbose:
        print(f"Got resources with version {resourceVersion}")
    setApplicationState(True)
    for resource in objects["items"]:
        process_resource(state=state, resource=resource, verbose=verbose)
    await reconcileCallback(state)

    w = watch.Watch()
    last_reconcile = time.perf_counter()
    need_reconcile = False
    print("Starting watch...")
    while True:
        try:
            async for event in w.stream(
                api.list_namespaced_custom_object,
                group=GROUP,
                version=VERSION,
                namespace=searchNamespace,
                plural=PLURAL,
                resource_version=resourceVersion,
                timeout_seconds=3600,
                _request_timeout=30
            ):
                if event["type"] == 'ADDED':
                    process_resource(
                        state=state, resource=event["raw_object"], verbose=verbose)
                elif event["type"] == "MODIFIED":
                    delete_resource(
                        state=state, resource=event["raw_object"], verbose=verbose)
                    process_resource(
                        state=state, resource=event["raw_object"], verbose=verbose)
                elif event["type"] == "DELETED":
                    delete_resource(
                        state=state, resource=event["raw_object"], verbose=verbose)
                else:
                    raise RuntimeError(
                        f"Unknown resource event {event["type"]}!")
                need_reconcile = True
                if time.perf_counter() - last_reconcile > 10:
                    await reconcileCallback(state)
                    last_reconcile = time.perf_counter()
        except TimeoutError:
            if verbose:
                print("Client timeout, starting new stream")
            if time.perf_counter() - last_reconcile > 10 and need_reconcile:
                await reconcileCallback(state)
                last_reconcile = time.perf_counter()
                need_reconcile = False
