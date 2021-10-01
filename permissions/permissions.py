from rest_framework import permissions


class CompanyUserPermission(permissions.BasePermission):
    """
    Permission check for company users
    """

    def has_permission(self, request, view):
        return request.user.is_company
