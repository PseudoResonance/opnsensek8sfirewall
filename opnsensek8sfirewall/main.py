import asyncio
import os
import json

from kubernetes_asyncio import config
from pyopnsense import firewall
from opnsensek8sfirewall import health
from .state import RawState
from .reconcile import reconcile
from .agones import watch_resources


def load_config(path):
    try:
        configPath = os.path.abspath(os.path.join(os.getcwd(), path))
        with open(configPath, "r") as file:
            return json.loads(file.read())
    except FileNotFoundError:
        raise ValueError(f"Config file not present at: {configPath}")


async def create_kubernetes_client(
    configPath: str | None = None, configContext: str | None = None
) -> None:
    if configPath is not None:
        await config.load_kube_config(config_file=configPath, context=configContext)
    else:
        config.load_incluster_config()


async def mainTask(configPath: str = "./config.json", dryRun=False, verbose=False) -> None:
    print("App started!")
    configPathEnv = os.getenv("CONFIG_PATH")
    if configPathEnv is not None and len(configPathEnv) > 0:
        configPath = configPathEnv
    config = load_config(configPath)
    opnsenseApiKey = None
    opnsenseApiSecret = None
    apiKeyEnv = os.getenv("API_KEY")
    if apiKeyEnv is not None and len(apiKeyEnv) > 0:
        opnsenseApiKey = apiKeyEnv
    else:
        opnsenseApiKey = config["opnsense"]["apiKey"]
    apiSecretEnv = os.getenv("API_SECRET")
    if apiSecretEnv is not None and len(apiSecretEnv) > 0:
        opnsenseApiSecret = apiSecretEnv
    else:
        opnsenseApiSecret = config["opnsense"]["apiSecret"]
    print("Starting OPNSense API client...")
    firewallClient = firewall.FirewallClient(
        opnsenseApiKey,
        opnsenseApiSecret,
        config["opnsense"]["endpoint"],
    )
    if "debugState" in config:
        print("Using debug state from config!")
        config["debugState"]["searchDomain"] = config["kubernetes"]["searchDomain"]
        await reconcile(
            firewallClient,
            config["opnsense"]["categoryName"],
            config["debugState"],
            dryRun,
            verbose,
        )
        print("Exiting")
        exit(0)
    else:
        async def reconcileFunc(state: RawState): return await reconcile(
            firewallClient, config["opnsense"]["categoryName"], state, dryRun, verbose)
        print("Creating Kubernetes API client...")
        await create_kubernetes_client(
            configPath=config["kubernetes"].get("kubeConfigPath"),
            configContext=config["kubernetes"].get("kubeConfigContext"),
        )
        await watch_resources(setApplicationState=health.setReady, reconcileCallback=reconcileFunc, searchDomain=config["kubernetes"]["searchDomain"], searchNamespace=config["kubernetes"]["namespace"], verbose=verbose)


async def tasks(configPath: str = "./config.json", dryRun=False, verbose=False) -> None:
    tasks = []
    tasks.append(mainTask(configPath=configPath,
                 dryRun=dryRun, verbose=verbose))
    tasks.append(health.run())
    await asyncio.gather(*tasks)


def main(configPath: str = "./config.json", dryRun=False, verbose=False) -> None:
    asyncio.run(tasks(configPath=configPath, dryRun=dryRun, verbose=verbose))
