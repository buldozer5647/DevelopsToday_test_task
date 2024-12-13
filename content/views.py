from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import IntegrityError

from .models import SpyCat, Mission, Target
from .serializers import SpyCatSerializer, MissionSerializer, TargetSerializer

class SpyCatListCreateView(APIView):
    def get(self, request):
        cats = SpyCat.objects.all()
        serializer = SpyCatSerializer(cats, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SpyCatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpyCatDetailView(APIView):
    def get_object(self, pk):
        try:
            return SpyCat.objects.get(pk=pk)
        except SpyCat.DoesNotExist:
            return None

    def get(self, request, pk):
        cat = self.get_object(pk)
        if not cat:
            return Response({"error": "Cat not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SpyCatSerializer(cat)
        return Response(serializer.data)

    def put(self, request, pk):
        cat = self.get_object(pk)
        if not cat:
            return Response({"error": "Cat not found"}, status=status.HTTP_404_NOT_FOUND)
        
        salary = request.data.get("salary")
        if salary is None:
            return Response({"error": "Only 'salary' can be updated."}, status=status.HTTP_400_BAD_REQUEST)

        cat.salary = salary
        cat.save()
        serializer = SpyCatSerializer(cat)
        return Response(serializer.data)

    def delete(self, request, pk):
        cat = self.get_object(pk)
        if not cat:
            return Response({"error": "Cat not found"}, status=status.HTTP_404_NOT_FOUND)
        cat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MissionListCreateView(APIView):
    def get(self, request):
        missions = Mission.objects.all()
        serializer = MissionSerializer(missions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MissionDetailView(APIView):
    def get_object(self, pk):
        try:
            return Mission.objects.get(pk=pk)
        except Mission.DoesNotExist:
            return None

    def get(self, request, pk):
        mission = self.get_object(pk)
        if not mission:
            return Response({"error": "Mission not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = MissionSerializer(mission)
        return Response(serializer.data)

    def put(self, request, pk):
        mission = self.get_object(pk)

        if not mission:
            return Response({"error": "Mission not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MissionSerializer(mission, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        mission = self.get_object(pk)
        if not mission:
            return Response({"error": "Mission not found"}, status=status.HTTP_404_NOT_FOUND)
        if mission.cat:
            return Response({"error": "Cannot delete a mission assigned to a cat"}, status=status.HTTP_400_BAD_REQUEST)
        mission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChangeTargetInfoView(APIView):
    def get_object(self, pk, pk_target):
        try:
            mission = Mission.objects.get(pk=pk)
            return mission.targets.get(pk=pk_target)
        except (Mission.DoesNotExist, Target.DoesNotExist):
            return None

    def get(self, request, pk, pk_target):
        target = self.get_object(pk, pk_target)

        if not target:
            return Response({"error": "Mission or target not found"}, status=status.HTTP_404_NOT_FOUND)
    
        serializer = TargetSerializer(target)

        return Response(serializer.data)
    
    def put(self, request, pk, pk_target):
        target = self.get_object(pk, pk_target)

        if not target:
            return Response({"error": "Mission or target not found"}, status=status.HTTP_404_NOT_FOUND)

        if target.is_completed:
            return Response({"error": "Target is already completed"}, status=status.HTTP_400_BAD_REQUEST)

        # i know it's not dry
        if not Mission.objects.get(pk=pk).cat:
            return Response({"error": "Assign a cat for work"}, status=status.HTTP_400_BAD_REQUEST)

        notes = request.data.get("notes")
        if notes is not None:
            target.notes = notes
            target.save()
            serializer = TargetSerializer(target)
            return Response(serializer.data)
        else:
            return Response({"error": "Notes field is required"}, status=status.HTTP_400_BAD_REQUEST)

class MarkTargetCompleteView(APIView):
    def post(self, request, pk, pk_target):
        try:
            mission = Mission.objects.get(pk=pk)
            target = mission.targets.get(pk=pk_target)
        except (Mission.DoesNotExist, Target.DoesNotExist):
            return Response({"error": "Mission or target not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not mission.cat:
            return Response({"error": "Assign a cat for work"}, status=status.HTTP_400_BAD_REQUEST)
        if not target.notes:
            return Response({"error": "Take notes before completing the target"}, status=status.HTTP_400_BAD_REQUEST)
        
        target.is_completed = True
        target.save()

        if all(t.is_completed for t in mission.targets.all()):
            mission.is_completed = True

            # One cat can only have one mission at a time
            mission.is_done_by = str(mission.cat.id) + " " + mission.cat.name
            mission.cat = None

            mission.save()

        return Response({
            "status": "Target marked as completed",
            "mission_completed": mission.is_completed
        })

class AssignCatToMissionView(APIView):
    def post(self, request, pk):
        try:
            mission = Mission.objects.get(pk=pk)
        except Mission.DoesNotExist:
            return Response({"error": "Mission not found"}, status=status.HTTP_404_NOT_FOUND)

        cat_id = request.data.get('cat_id')
        try:
            cat = SpyCat.objects.get(id=cat_id)
        except SpyCat.DoesNotExist:
            return Response({"error": "Cat not found"}, status=status.HTTP_404_NOT_FOUND)

        if mission.cat:
            return Response({"error": "Mission already assigned to a cat"}, status=status.HTTP_400_BAD_REQUEST)

        if mission.is_completed:
            return Response({"error": "Cannot assign a cat to a completed mission"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            mission.cat = cat
            mission.save()
        except IntegrityError:
            return Response({"error": "This cat already has a mission"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = MissionSerializer(mission)
        
        return Response(serializer.data)
