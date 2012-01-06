import zope.component
from zope.authentication.interfaces import IAuthentication
from zope.app.component import hooks


def getPrincipalTitle(principal_id):
    pau = zope.component.queryUtility(
        IAuthentication,
        context = hooks.getSite()
        )
    try:
        title = pau.getPrincipal(principal_id).title
        return title
    except Exception:
        return principal_id
