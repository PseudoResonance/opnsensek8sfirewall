
from pyopnsense import firewall
from .alias import ensure_aliases, ensure_port_aliases, delete_old_aliases
from .state import process_raw_state
from .nat import ensure_nat
from .filter import ensure_filter


async def reconcile(
    firewallClient: firewall.FirewallClient,
    firewallCategoryName: str,
    state,
    dryRun=False,
    verbose=False,
) -> None:
    categories = firewallClient.get_categories()
    categoryUuid = None
    for row in categories["rows"]:
        if row["name"] == firewallCategoryName:
            categoryUuid = row["uuid"]
            break
    if categoryUuid is None:
        raise RuntimeError(
            f"Unable to find firewall category {firewallCategoryName}")
    if verbose:
        print(f"Identified category UUID: {categoryUuid}")
    targetState = process_raw_state(state)
    old_aliases = ensure_aliases(
        firewallClient,
        categoryUuid,
        targetState,
        dryRun,
        verbose,
    )
    old_port_aliases = ensure_port_aliases(
        firewallClient,
        categoryUuid,
        targetState,
        dryRun,
        verbose,
    )
    # ensure_nat(firewallClient, categoryUuid, targetConfig, dryRun, verbose)
    # ensure_filter(firewallClient, categoryUuid, targetConfig, dryRun, verbose)
    # delete_old_aliases(
    #     firewallClient, old_aliases, dryRun, verbose
    # )  # Aliases cannot be deleted while still in use, so after we have deleted any old filters, go back and delete the old aliases
    # delete_old_aliases(
    #     firewallClient, old_port_aliases, dryRun, verbose
    # )  # Aliases cannot be deleted while still in use, so after we have deleted any old filters, go back and delete the old aliases
    if dryRun:
        print("Applying changes to aliases")
    else:
        result = firewallClient.apply_aliases()
        if verbose:
            print(result)
