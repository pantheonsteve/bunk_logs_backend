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
        fields = ["id","bunk", "camper"]


class BunkLogSerializer(serializers.ModelSerializer):
    """
    Serializer for BunkLog model.
    For POST requests, you need to provide:
    - date
    - bunk_assignment (id)
    - counselor (id)
    - other fields as needed
    """
    class Meta:
        model = BunkLog
        fields = '__all__'
        
    def validate(self, data):
        """
        Validate the BunkLog data.
        """
        # Validate scores are between 1 and 5 if provided
        for score_field in ['social_score', 'behavior_score', 'participation_score']:
            if score_field in data and data[score_field] is not None:
                score = data[score_field]
                if score < 1 or score > 5:
                    raise serializers.ValidationError({score_field: "Score must be between 1 and 5"})
        
        # Check for duplicate bunk logs (same camper on same date)
        if self.instance is None:  # Only for creation, not updates
            existing = BunkLog.objects.filter(
                bunk_assignment=data['bunk_assignment'],
                date=data['date']
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    "A bunk log already exists for this camper on this date."
                )
                
        return data
    
class CamperBunkLogSerializer(serializers.ModelSerializer):
    """
    Serializer for bunklogs related to a specific camper.
    """
    camper = serializers.SerializerMethodField()
    bunk = BunkSerializer(read_only=True)
    bunk_assignment = CamperBunkAssignmentSerializer(read_only=True)

    class Meta:
        model = BunkLog
        fields = [
            "date",
            "bunk",
            "counselor",
            "not_on_camp",
            "social_score",
            "behavior_score",
            "participation_score",
            "request_camper_care_help",
            "request_unit_head_help",
            "description",
            "camper",
            "bunk_assignment",
            "id"
        ]
    
    def get_camper(self, obj):
        return CamperSerializer(obj.bunk_assignment.camper).data
    
    def get_bunk(self, obj):
        return BunkSerializer(obj.bunk_assignment.bunk).data

