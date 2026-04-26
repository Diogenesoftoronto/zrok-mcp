from mcp.server.fastmcp import FastMCP

mcp = FastMCP("zrok", instructions="""Zrok MCP server for managing secure tunnels and shares.

This server provides tools to manage zrok environments, create/access shares,
and view account status. Requires zrok2 CLI installed and a zrok account.

Each tool accepts an `action` parameter that selects the operation:
  zrok_env:    status | enable | disable
  zrok_share:  create | delete | list
  zrok_access: create | delete | list""")


def _root():
    from zrok2.environment import root as root_mod

    return root_mod.Load()


_SHARE_MODES = {"public", "private"}
_BACKEND_MODES = {"proxy", "web", "tcpTunnel", "udpTunnel", "caddy", "drive", "socks"}


# ── Environment ──────────────────────────────────────────────────────────


@mcp.tool()
def zrok_env(action: str, token: str = "", description: str = "") -> dict:
    """Manage the zrok environment: check status, enable, or disable.

    Args:
        action: Operation to perform — "status", "enable", or "disable".
        token: Account enable token (required when action is "enable").
        description: Optional environment description (used with "enable").
    """
    if action == "status":
        from zrok2 import status as status_mod

        try:
            root = _root()
            s = status_mod.status(root)
            return {
                "enabled": s.Enabled,
                "api_endpoint": s.ApiEndpoint,
                "api_endpoint_source": s.ApiEndpointSource,
                "token": s.Token[:8] + "..." if s.Token else "",
                "ziti_identity": s.ZitiIdentity[:8] + "..." if s.ZitiIdentity else "",
            }
        except Exception as e:
            return {"enabled": False, "error": str(e)}

    elif action == "enable":
        from zrok2.environment.enable import enable

        try:
            root = _root()
            enable(root, token=token, description=description)
            return {"success": True, "message": "Environment enabled"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif action == "disable":
        from zrok2.environment.enable import disable

        try:
            root = _root()
            disable(root)
            return {"success": True, "message": "Environment disabled"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    else:
        return {"error": f"Unknown action '{action}'. Use: status, enable, disable"}


# ── Shares ────────────────────────────────────────────────────────────────


@mcp.tool()
def zrok_share(
    action: str,
    target: str = "",
    share_mode: str = "public",
    backend_mode: str = "proxy",
    frontend: str = "public",
    basic_auth: list[str] | None = None,
    reserved: bool = False,
    unique_name: str = "",
    permission_mode: str = "open",
    oauth_provider: str = "",
    oauth_email_patterns: list[str] | None = None,
    share_token: str = "",
    share_mode_filter: str | None = None,
    backend_mode_filter: str | None = None,
) -> dict:
    """Manage zrok shares: create, delete, or list.

    Args:
        action: Operation to perform — "create", "delete", or "list".
        target: The local resource to share, e.g. "http://localhost:8080" (create).
        share_mode: "public" or "private" (create).
        backend_mode: Content handling mode: proxy, web, tcpTunnel, udpTunnel, caddy, drive, socks (create).
        frontend: Frontend name for public shares (create).
        basic_auth: List of "user:password" strings for auth protection (create).
        reserved: If True, create a reserved share with persistent subdomain (create).
        unique_name: Unique name for a reserved share, used as subdomain (create).
        permission_mode: "open" or "closed" — closed requires access grants (create).
        oauth_provider: OAuth provider for auth, e.g. "google" (create).
        oauth_email_patterns: Email patterns allowed via OAuth, e.g. ["*@example.com"] (create).
        share_token: Token of the share to delete (delete).
        share_mode_filter: Filter shares by mode — "public" or "private" (list).
        backend_mode_filter: Filter shares by backend mode (list).
    """
    if action == "create":
        from zrok2 import share as share_mod
        from zrok2.model import ShareRequest

        if share_mode not in _SHARE_MODES:
            return {"success": False, "error": f"Invalid share_mode: {share_mode}. Must be one of {_SHARE_MODES}"}
        if backend_mode not in _BACKEND_MODES:
            return {"success": False, "error": f"Invalid backend_mode: {backend_mode}. Must be one of {_BACKEND_MODES}"}
        try:
            root = _root()
            request = ShareRequest(
                BackendMode=backend_mode,
                ShareMode=share_mode,
                Target=target,
                Frontends=[frontend] if share_mode == "public" else [],
                BasicAuth=basic_auth or [],
                Reserved=reserved,
                UniqueName=unique_name,
                PermissionMode=permission_mode,
                OauthProvider=oauth_provider,
                OauthEmailAddressPatterns=oauth_email_patterns or [],
            )
            shr = share_mod.CreateShare(root=root, request=request)
            return {
                "success": True,
                "token": shr.Token,
                "frontend_endpoints": shr.FrontendEndpoints,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif action == "delete":
        from zrok2 import share as share_mod
        from zrok2.model import Share

        try:
            root = _root()
            shr = Share(Token=share_token, FrontendEndpoints=[])
            share_mod.DeleteShare(root=root, shr=shr)
            return {"success": True, "message": f"Share {share_token} deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif action == "list":
        from zrok2 import listing

        try:
            root = _root()
            filters = {}
            if share_mode_filter:
                filters["share_mode"] = share_mode_filter
            if backend_mode_filter:
                filters["backend_mode"] = backend_mode_filter
            shares = listing.list_shares(root, **filters)
            return {
                "shares": [
                    {
                        "token": s.Token,
                        "share_mode": s.ShareMode,
                        "backend_mode": s.BackendMode,
                        "target": s.Target,
                        "frontend_endpoints": s.FrontendEndpoints,
                        "limited": s.Limited,
                        "created_at": s.CreatedAt,
                        "updated_at": s.UpdatedAt,
                    }
                    for s in shares
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    else:
        return {"error": f"Unknown action '{action}'. Use: create, delete, list"}


# ── Access ───────────────────────────────────────────────────────────────


@mcp.tool()
def zrok_access(
    action: str,
    share_token: str = "",
    access_token: str = "",
    backend_mode: str = "proxy",
) -> dict:
    """Manage zrok access to shares: create, delete, or list.

    Args:
        action: Operation to perform — "create", "delete", or "list".
        share_token: The share token to access (create, delete, or filter by in list).
        access_token: The access token to remove (delete).
        backend_mode: Backend mode of the access: proxy, web, tcpTunnel, etc. (delete).
    """
    if action == "create":
        from zrok2 import access as access_mod
        from zrok2.model import AccessRequest

        try:
            root = _root()
            request = AccessRequest(ShareToken=share_token)
            acc = access_mod.CreateAccess(root=root, request=request)
            return {
                "success": True,
                "token": acc.Token,
                "share_token": acc.ShareToken,
                "backend_mode": acc.BackendMode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif action == "delete":
        from zrok2 import access as access_mod
        from zrok2.model import Access

        try:
            root = _root()
            acc = Access(Token=access_token, ShareToken=share_token, BackendMode=backend_mode)
            access_mod.DeleteAccess(root=root, acc=acc)
            return {"success": True, "message": f"Access to share {share_token} deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif action == "list":
        from zrok2 import listing

        try:
            root = _root()
            filters = {}
            if share_token:
                filters["share_token"] = share_token
            accesses = listing.list_accesses(root, **filters)
            return {
                "accesses": [
                    {
                        "id": a.Id,
                        "frontend_token": a.FrontendToken,
                        "share_token": a.ShareToken,
                        "backend_mode": a.BackendMode,
                        "bind_address": a.BindAddress,
                        "description": a.Description,
                        "limited": a.Limited,
                        "created_at": a.CreatedAt,
                        "updated_at": a.UpdatedAt,
                    }
                    for a in accesses
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    else:
        return {"error": f"Unknown action '{action}'. Use: create, delete, list"}


# ── Entry Point ──────────────────────────────────────────────────────────


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
