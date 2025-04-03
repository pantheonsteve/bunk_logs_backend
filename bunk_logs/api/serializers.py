from campers.models import Camper
from campers.models import CamperBunkAssignment
from rest_framework import serializers

from bunk_logs.users.models import User
from bunks.models import Bunk
from bunks.models import Cabin
from bunks.models import Session
from bunks.models import Unit
from bunklogs.models import BunkLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "role", "id"]


class CabinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabin
        fields = "__all__"


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = "__all__"


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = "__all__"


class BunkSerializer(serializers.ModelSerializer):
    unit = UnitSerializer()
    cabin = CabinSerializer()
    session = SessionSerializer()
    counselors = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Bunk
        fields = "__all__"


class CamperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camper
        fields = "__all__"


class CamperBunkAssignmentSerializer(serializers.ModelSerializer):
    bunk = BunkSerializer()
    camper = CamperSerializer()

    class Meta:
        model = CamperBunkAssignment
        fields = ["bunk", "camper"]


class BunkLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BunkLog
        fields = '__all__'
