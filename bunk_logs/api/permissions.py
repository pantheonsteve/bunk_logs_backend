from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class IsCounselorForBunk(permissions.BasePermission):
    """
    Permission to only allow counselors to access their own bunks.
    """
    def has_permission(self, request, view):
        # Log all view kwargs for debugging
        logger.debug(f"View kwargs: {view.kwargs}")
        
        # Anonymous users have no access
        if not request.user.is_authenticated:
            logger.debug(f"Permission denied: User not authenticated")
            return False
        
        # Staff/admin users always have access
        logger.debug(f"User: {request.user.email}, Staff: {request.user.is_staff}, Role: {request.user.role}")
        if request.user.is_staff or request.user.role == 'Admin':
            logger.debug(f"Access granted to admin/staff: {request.user.email}")
            return True
        
        # Look for bunk_id in URL parameters
        bunk_id = None
        if 'bunk_id' in view.kwargs:
            bunk_id = view.kwargs['bunk_id']
        elif 'pk' in view.kwargs:
            bunk_id = view.kwargs['pk']
        
        if not bunk_id:
            logger.debug("No bunk_id found in view kwargs")
            return False
        
        logger.debug(f"Found bunk_id: {bunk_id}")
        
        # Unit heads can access bunks in their units
        if request.user.role == 'Unit Head':
            from bunks.models import Bunk
            has_access = Bunk.objects.filter(
                id=bunk_id, 
                unit__unit_head=request.user
            ).exists()
            logger.debug(f"Unit Head access to bunk {bunk_id}: {has_access}")
            return has_access
        
        # Counselors can access their assigned bunks
        if request.user.role == 'Counselor':
            from bunks.models import Bunk
            has_access = Bunk.objects.filter(
                id=bunk_id, 
                counselors__id=request.user.id
            ).exists()
            
            logger.debug(f"Counselor access to bunk {bunk_id}: {has_access}")
            
            # Log all assigned bunks for debugging
            assigned_bunk_ids = list(Bunk.objects.filter(counselors__id=request.user.id).values_list('id', flat=True))
            logger.debug(f"User is assigned to bunk IDs: {assigned_bunk_ids}")
            
            return has_access
        
        # Default deny
        logger.debug(f"Permission denied for user {request.user.email} with role {request.user.role}")
        return False


class DebugPermission(permissions.BasePermission):
    """
    Temporary debug permission that allows everything but logs details.
    Use this temporarily to debug permission issues.
    """
    def has_permission(self, request, view):
        logger.debug(f"DEBUG PERMISSION CHECK")
        
        # Check if user is authenticated before accessing email
        if request.user.is_authenticated:
            logger.debug(f"User: {request.user.email}, authenticated: True")
        else:
            logger.debug(f"User: AnonymousUser, authenticated: False")
            
        logger.debug(f"View kwargs: {view.kwargs}")
        logger.debug(f"View class: {view.__class__.__name__}")
        logger.debug(f"Request path: {request.path}")
        
        # Always allow access for debugging
        return True


class UnitHeadPermission(permissions.BasePermission):
    """
    Permission to allow unit heads to access their units' bunks.
    """
    def has_permission(self, request, view):
        # Staff/admin users always have access
        if request.user.is_staff or request.user.role == 'Admin':
            return True
        
        # Only unit heads have access
        if request.user.role != 'Unit Head':
            return False
        
        # Get bunk_id from URL parameters
        bunk_id = view.kwargs.get('bunk_id')
        if not bunk_id:
            return False
        
        # Check if the bunk belongs to a unit managed by this unit head
        from bunks.models import Bunk
        return Bunk.objects.filter(
            id=bunk_id, 
            unit__unit_head=request.user
        ).exists()


class CamperCarePermission(permissions.BasePermission):
    """
    Permission to allow camper care staff to access all bunks.
    """
    def has_permission(self, request, view):
        # Staff/admin users always have access
        if request.user.is_staff or request.user.role == 'Admin':
            return True
        
        # Check if user is camper care
        return request.user.role == 'Camper Care'