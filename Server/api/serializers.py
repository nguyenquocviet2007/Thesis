from rest_framework import serializers
from .models import Student, Assignment, Course

      
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        
class StudentSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)
    class Meta:
        model = Student
        fields = ["id", "studentId", "fullname", "password", "role", "courses"]
        extra_kwargs = {
            "password": {"write_only": True},
        }
        
class AssignmentSerializer(serializers.ModelSerializer): 
    id = serializers.ReadOnlyField()
    courses = CourseSerializer(many=True)
    class Meta:
        model = Assignment
        fields = ["id", "title", "key", "question", "answer", "user_answer", "created_at", "result", "status", "url", "student", "courses", "reason", "description"]