from campers.models import Camper
from campers.models import CamperBunkAssignment
from rest_framework import viewsets

from bunks.models import Bunk
from bunks.models import Unit

from .serializers import BunkSerializer
from .serializers import CamperBunkAssignmentSerializer
from .serializers import CamperSerializer
from .serializers import UnitSerializer


class BunkViewSet(viewsets.ModelViewSet):
    queryset = Bunk.objects.all()
    serializer_class = BunkSerializer


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class CamperViewSet(viewsets.ModelViewSet):
    queryset = Camper.objects.all()
    serializer_class = CamperSerializer


class CamperBunkAssignmentViewSet(viewsets.ModelViewSet):
    queryset = CamperBunkAssignment.objects.all()
    serializer_class = CamperBunkAssignmentSerializer


# Create your views here.
