from rest_framework import permissions

COMPANY_METHODS = ["POST", "PATCH", "DELETE"]


class CompanyUserPermission(permissions.BasePermission):
    """
    Permission check for company users
    """

    def has_permission(self, request, view):
        if request.method in COMPANY_METHODS:
            return request.user.is_company
        else:
            return True
