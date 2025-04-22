from campers.models import Camper
from campers.models import CamperBunkAssignment
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny

from bunks.models import Bunk
from bunks.models import Unit
from bunklogs.models import BunkLog
from .serializers import BunkLogSerializer

from .serializers import BunkSerializer
from .serializers import CamperBunkAssignmentSerializer
from .serializers import CamperSerializer
from .serializers import UnitSerializer
from .serializers import CamperBunkLogSerializer


class BunkViewSet(viewsets.ModelViewSet):
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]
    queryset = Bunk.objects.all()
    serializer_class = BunkSerializer


class BunkLogsInfoByDateViewSet(APIView):
    """
    API view to get bunk logs info by date.

    The endpoint will be '/api/v1/bunklogs/<str:bunk_id>/logs/<str:date>/'
    where 'bunk_id' is the ID of the bunk and 'date' is the date in YYYY-MM-DD format.
    The response will first search for all of the bunk_assignemnts for the bunk on that date.
    Then, it will search for all of the bunk logs for those assignments.
    The response will include the bunk assignment ID and the bunk log ID.
    If no bunk logs are found, the response will return an empty list.
    The response will be in the following format:
        {
            "date": str in YYYY-MM-DD format,
            "bunk": {
                "id": str,
                "name": str,
                "is_active": bool,
                "start_date": str in YYYY-MM-DD format,
                "end_date": str in YYYY-MM-DD format,
            },
            "unit": {
                "id": str,
                "name": str,
                "is_active": bool,
                "start_date": str in YYYY-MM-DD format,
                "end_date": str in YYYY-MM-DD format,
                "unit_id": str,
                "unir_head": str,
                "unit_head_id": str,
                "unit_head_email": str,
            },
            "campers": [
                {
                    "camper_id": str,
                    "camper_first_name": str,
                    "camper_last_name": str,
                    "bunk_log": {
                        "id": str,
                        "date": str in YYYY-MM-DD format,
                        "bunk_assignment_id": str,
                        "counselor": str,
                        "social_score": int,
                        "behavior_score": int,
                        "participation_score": int,
                        "request_camper_care_help": bool,
                        "request_unit_head_help": bool,
                        "description": text
                    },
                    "bunk_assignment": {
                        "id": str,
                        "camper_id": str,
                        "bunk_name": str,
                        "is_active": bool,
                        "start_date": str in YYYY-MM-DD format,
                        "end_date": str in YYYY-MM-DD format,
                        "bunk_assignment_id": str,
                    }
                },
            ],
            "counserlors": [
                {
                    "id": str,
                    "first_name": str,
                    "last_name": str,
                    "email": str,
                    "phone_number": str,
                },
            ],
        },
    """
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]

    def get(self, request, bunk_id, date):
        try:
            # Get the bunk
            bunk = Bunk.objects.get(id=bunk_id)
            serialized_bunk = BunkSerializer(bunk).data
            
            # Get the unit
            unit = Unit.objects.filter(bunks=bunk).first()
            serialized_unit = UnitSerializer(unit).data if unit else None
            
            # Get camper assignments for this bunk
            assignments = CamperBunkAssignment.objects.filter(
                bunk=bunk,
                is_active=True,
            ).select_related('camper')
            
            # Get bunk logs for these assignments on the given date
            
            campers_data = []
            for assignment in assignments:
                # Get bunk log for this assignment and date (if exists)
                try:
                    bunk_log = BunkLog.objects.get(
                        bunk_assignment=assignment,
                        date=date
                    )
                    serialized_log = BunkLogSerializer(bunk_log).data
                except BunkLog.DoesNotExist:
                    serialized_log = None
                
                # Add to campers list
                campers_data.append({
                    "camper_id": str(assignment.camper.id),
                    "camper_first_name": assignment.camper.first_name,
                    "camper_last_name": assignment.camper.last_name,
                    "bunk_log": serialized_log,
                    "bunk_assignment": CamperBunkAssignmentSerializer(assignment).data
                })
            
            # Get counselors for this bunk
            # Implement this based on your data model
            counselors_data = []  # You'll need to implement this part

            for counselor in bunk.counselors.all():
                counselors_data.append({
                    "id": str(counselor.id),
                    "first_name": counselor.first_name,
                    "last_name": counselor.last_name,
                    "email": counselor.email,
                })
            
            response_data = {
                "date": date,
                "bunk": serialized_bunk,
                "unit": serialized_unit,
                "campers": campers_data,
                "counselors": counselors_data
            }
            
            return Response(response_data)
            
        except Bunk.DoesNotExist:
            return Response({"error": f"Bunk with ID {bunk_id} not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class UnitViewSet(viewsets.ModelViewSet):
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class CamperViewSet(viewsets.ModelViewSet):
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]
    queryset = Camper.objects.all()
    serializer_class = CamperSerializer


class CamperBunkAssignmentViewSet(viewsets.ModelViewSet):
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]
    queryset = CamperBunkAssignment.objects.all()
    serializer_class = CamperBunkAssignmentSerializer


class BunkLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for creating, reading, updating and deleting BunkLogs.
    
    POST requests to this endpoint should include:
    - date: YYYY-MM-DD format
    - bunk_assignment: ID of the CamperBunkAssignment
    - counselor: ID of the counselor User
    - not_on_camp: Boolean indicating if camper is not on camp
    - social_score: Integer 1-5 (optional)
    - behavior_score: Integer 1-5 (optional)
    - participation_score: Integer 1-5 (optional)
    - request_camper_care_help: Boolean
    - request_unit_head_help: Boolean
    - description: Text description
    """
    #renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]  # Consider using proper authentication here
    queryset = BunkLog.objects.all()
    serializer_class = BunkLogSerializer


class CamperBunkLogViewSet(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]
    queryset = BunkLog.objects.all()
    serializer_class = BunkLogSerializer

    def get(self, request, camper_id):
        try:
            # Get the camper
            camper = Camper.objects.get(id=camper_id)
            serialized_camper = CamperSerializer(camper).data
            # Get the bunk assignments for this camper
            assignments = CamperBunkAssignment.objects.filter(camper=camper)
            # Get the bunk logs for these assignments
            bunk_logs = BunkLog.objects.filter(
                bunk_assignment__in=assignments
            ).select_related('bunk_assignment__bunk')
            # Serialize the bunk logs
            serialized_bunk_logs = CamperBunkLogSerializer(bunk_logs, many=True).data
            # Prepare the response data
            response_data = {
                "camper": serialized_camper,
                "bunk_logs": serialized_bunk_logs,
                "bunk_assignments": [
                    {
                        "id": str(assignment.id),
                        "bunk_name": assignment.bunk.name,
                        "bunk_id": str(assignment.bunk.id),
                        "is_active": assignment.is_active,
                        "start_date": assignment.start_date,
                        "end_date": assignment.end_date,
                    }
                    for assignment in assignments
                ],
            }
            return Response(response_data)
        except Camper.DoesNotExist:
            return Response({"error": f"Camper with ID {camper_id} not found"}, status=404)
# Create your views here.
