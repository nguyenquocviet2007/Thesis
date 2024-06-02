import http.cookies
import os
import boto3
import string
import random
import psycopg2
import jwt
import http
import itertools
from datetime import datetime
from .models import Student, Assignment, Course
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password, check_password
from .serializers import StudentSerializer, AssignmentSerializer, CourseSerializer
from .utils import AccessToken, RefreshToken
from dotenv import load_dotenv
from langchain_community.document_loaders.s3_file import S3FileLoader 
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter #TextSplitter
from langchain_text_splitters import Language
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain.evaluation import load_evaluator

load_dotenv()
# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        data = {
            "studentId": request.data['studentId'].lower(),
            "password": make_password(request.data['password']),
            "fullname": request.data['fullname']
        }    
        serializer = StudentSerializer(data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = Response()
            response.data = {
                "message": "Register Successfully!",
                }
            return response
        else:
            return Response({
                "message": "error",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
    
class LoginView(APIView):
    def post(self, request):
        student_id = request.data['studentId'].lower()
        password = request.data['password']

        connection = psycopg2.connect(database='qgae', user='qgae', password='quocviet01', host='localhost', port='5432')
        connection.autocommit = True
        cursor = connection.cursor()
        get_password_query = '''SELECT password FROM api_student WHERE "studentId" = %s'''
        get_password = (student_id, )
        cursor.execute(get_password_query, get_password)
        student = cursor.fetchone()
        
        get_student_data_query = '''SELECT * FROM api_student WHERE "studentId" = %s'''
        get_student_data = (student_id, )
        cursor.execute(get_student_data_query, get_student_data)
        student_data = cursor.fetchone()
        
        cursor.close()
        
        if student is None:
            raise AuthenticationFailed('Invalid Student ID or Password')
        
        if not check_password(password, student[0]):
            raise AuthenticationFailed('Invalid Student ID or Password')
        
        access_token = AccessToken(student_id, student_data[0], student_data[-1])
        refresh_token = RefreshToken(student_id, student_data[0], student_data[-1])
        response = Response()
        response.set_cookie(key='access', value=access_token, httponly=True)
        response.set_cookie(key='refresh', value=refresh_token, httponly=True)
        response.data = {
            "message": "Login Successfully!",
            "access": access_token,
            "refresh": refresh_token,
            "data": student_data
        }        
        return response
    
class RegenerateAccessTokenView(APIView):
    def get(self, request):
        try:
            refreshToken = request.COOKIES('refresh')
            if not refreshToken:
                return Response({
                    "message": "Invalid Token"
                }, status=status.HTTP_401_UNAUTHORIZED)
            else:
                payload = jwt.decode(refreshToken, os.environ.get('REFRESH_TOKEN'), algorithms='HS256')
                newToken = jwt.encode(payload, os.environ.get('ACCESS_TOKEN'), algorithm='HS256')
                return Response({
                    "access": newToken
                })
        except Exception as error:
            raise error
        
        
class SubmitAssignment(APIView):  
    def put(self, request, id = None):
        token = request.META.get('HTTP_AUTHORIZATION')[7:]
        
        if not token:
            raise AuthenticationFailed('UnAuthorized')
        try:
            payload = jwt.decode(token, os.environ.get('ACCESS_TOKEN'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthorized')
        
        codeFile = request.FILES['file']
        assignment_id = id
        studentId = payload['id']
      
        accessKey = os.environ.get('AWS_SECRET_ACCESS_KEY')
        secretKey = os.environ.get('AWS_ACCESS_KEY_ID')
        bucketName = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        regionName = os.environ.get('AWS_S3_REGION_NAME')
            
            #Upload code file and store on AWS S3 with boto3
        s3 = boto3.client('s3', aws_access_key_id = secretKey, aws_secret_access_key = accessKey)
        letters = string.ascii_lowercase
        key = ''.join(random.choice(letters) for i in range(10))
        s3.upload_fileobj(codeFile, 'qagen', key)
        #load code file from AWS S3
        loader = S3FileLoader(
            bucket=bucketName,
            key=key,
            region_name=regionName,
            aws_access_key_id= secretKey,
            aws_secret_access_key= accessKey
        )
            
        documents = loader.load()
        os.environ["OPENAI_API_KEY"] = os.environ.get('OPENAI_API_KEY')
            
            
        splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, chunk_size = 2000, chunk_overlap = 200)
        texts = splitter.split_documents(documents=documents)
            
        db = Chroma.from_documents(texts, OpenAIEmbeddings())
        retriever = db.as_retriever(
            search_type = 'mmr',
            search_kwargs = {"k": 8}
        )
            
        qa_interface = ChatOpenAI(model_name="gpt-3.5-turbo-1106")
            
        promt = ChatPromptTemplate.from_messages(
            [
                ("user", "{input}"),
                (
                    "user",
                        "Given the above conversation, generate a search query to look up to get information relevant to the conversation"
                    )
                ]
            )
            
        retriever_chain = create_history_aware_retriever(qa_interface, retriever, promt)
            
        promt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Answer the user's questions based on the below context: {context}"
                ),
                ("user", "{input}")
            ]
        )
        documents_chain = create_stuff_documents_chain(qa_interface, promt)
            
        qa = create_retrieval_chain(retriever_chain, documents_chain)
        question_promt = "List 3 questions related to the given code"
        questions = qa.invoke({"input": question_promt})["answer"]
        questionsArray = questions.splitlines()            
        answersArray = []
        for question in questionsArray:
            answers = qa.invoke({"input": question})
            answersArray.append(answers['answer'])
            
        #insert question into database
        data = {
            "key": key,
            "question": questionsArray,
            "answer": answersArray,
            "url": f"https://qagen.s3.ap-southeast-2.amazonaws.com/{key}",
            "student": studentId
        }
        id = Assignment.objects.get(id=id)
        serializer = AssignmentSerializer(id, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({
                "message": "error",
                "data": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST)
        
        assignment = Assignment.objects.filter(key = key).first()
        if(assignment):
            serializer = AssignmentSerializer(assignment)
            data = {
                "id": serializer.data['id'],
                "title": serializer.data['title'],
                "key": serializer.data['key'],
                "question": serializer.data['question'],
                "created_at": serializer.data['created_at'],
                "url": serializer.data['url']
            }
            return Response(data, status=status.HTTP_201_CREATED)
        
        
class UploadQuestion(APIView):
    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')[7:]
        
        if not token:
            raise AuthenticationFailed('UnAuthorized')
        try:
            payload = jwt.decode(token, os.environ.get('ACCESS_TOKEN'), algorithms=['HS256'])
            if payload['role'] != 'lecturer':
                raise AuthenticationFailed('UnAuthorized')
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthorized')

        courseCode = request.GET.get('course_code')
        
        course = Course.objects.filter(course_code = courseCode)
        
        if course:
            serializer = CourseSerializer(course, many=True)
            courseId = serializer.data[0]['id']
        
        title = request.data['title']
        description = request.data['description']
        due_date = request.data['due_date']
        created_at = datetime.now()
        status = 'Pending'
        connection = psycopg2.connect(database='qgae', user='qgae', password='quocviet01', host='localhost', port='5432')
        connection.autocommit = True
        cursor = connection.cursor()
        insert_assignment_table_query = '''INSERT INTO api_assignment (title, description, due_date, created_at, status) VALUES (%s, %s, %s, %s, %s)'''
        insert_assignment_table = (title, description, due_date, created_at, status)
        cursor.execute(insert_assignment_table_query, insert_assignment_table)
        get_assignment_id_query = '''SELECT id from api_assignment WHERE "title" = %s'''
        get_assignment_id = (title, )
        cursor.execute(get_assignment_id_query, get_assignment_id)
        assignment_id = cursor.fetchone()
        assignmentId = assignment_id[0]
        
        insert_assignment_course_table_query = '''INSERT INTO api_assignment_courses (assignment_id, course_id) VALUES (%s, %s)'''
        insert_assignment_course_table = (assignmentId, courseId)
        cursor.execute(insert_assignment_course_table_query, insert_assignment_course_table)
        
        cursor.close()
        
        return Response({
            "message": "Upload Successfully!"
        }, status=status.HTTP_201_CREATED)
        
                
class GetAssignments(APIView):
    def get(self, request, id=None):
        token = request.META.get('HTTP_AUTHORIZATION')[7:]
        if not token:
            raise AuthenticationFailed('UnAuthorized')
        try:
            payload = jwt.decode(token, os.environ.get('ACCESS_TOKEN'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthorized')

    
        courses_code = id
        print(courses_code)
        connection = psycopg2.connect(database='qgae', user='qgae', password='quocviet01', host='localhost', port='5432')
        connection.autocommit = True
        cursor = connection.cursor()
        get_courses_id_query = '''SELECT id FROM api_course WHERE "course_code" = %s'''
        get_courses_id = (courses_code, )
        cursor.execute(get_courses_id_query, get_courses_id)
        courses_id = cursor.fetchall()
        course_id = list(itertools.chain.from_iterable(courses_id))
        get_assignments_courses_query = '''SELECT api_assignment.*
                                            FROM api_assignment
                                            INNER JOIN api_assignment_courses
                                            ON api_assignment.id = api_assignment_courses.assignment_id
                                            AND api_assignment_courses.course_id = %s'''
        get_assignment_courses = (course_id[0], )
        cursor.execute(get_assignments_courses_query, get_assignment_courses)
        assignments = cursor.fetchall()
        cursor.close()
        
        return Response(assignments, status=status.HTTP_200_OK)

class GetAssignment(APIView):
    def get(self, request, id=None):
        token = request.META.get('HTTP_AUTHORIZATION')[7:]

        if not token:
            raise AuthenticationFailed('UnAuthorized')
        try:
            payload = jwt.decode(token, os.environ.get('ACCESS_TOKEN'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthorized')
        
        assignment_id = Assignment.objects.filter(id=id).first()
        
        data = []
        if assignment_id:
            serializer = AssignmentSerializer(assignment_id)
            data.append(serializer.data)
            return Response(data, status = status.HTTP_200_OK)
        else:
            return Response({
                "message": "Assignment Is Empty!"
            }, status=status.HTTP_404_NOT_FOUND)
            
class GetAllAssignments(APIView):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')[7:]
        if not token:
            raise AuthenticationFailed('UnAuthorized')
        try:
            payload = jwt.decode(token, os.environ.get('ACCESS_TOKEN'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthorized')

    
        connection = psycopg2.connect(database='qgae', user='qgae', password='quocviet01', host='localhost', port='5432')
        connection.autocommit = True
        cursor = connection.cursor()
        get_assignment_query = '''SELECT * FROM api_assignment'''
        cursor.execute(get_assignment_query)
        assignments = cursor.fetchall()
        cursor.close()
        
        return Response(assignments, status=status.HTTP_200_OK)

class AnswerView(APIView):
    def put(self, request, id=None):
        token = request.META.get('HTTP_AUTHORIZATION')[7:]
        
        if not token:
            raise AuthenticationFailed('UnAuthorized')
        try:
            payload = jwt.decode(token, os.environ.get('ACCESS_TOKEN'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthorized')
        
        
        
        answer = request.data
        updateStatus = 'Done'
        updateData = {
            "user_answer": answer,
            "status": updateStatus
        }
        id = Assignment.objects.get(id=id)
        serializer = AssignmentSerializer(id, data=updateData, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Your answers are saved",
                "your_answer": serializer.data
            },
            status = status.HTTP_200_OK)
        else:
            return Response({
                "message": "error",
                "data": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST)

class ResultView(APIView):
    def put(self, request, id=None):
        token = request.META.get('HTTP_AUTHORIZATION')[7:]
        
        if not token:
            raise AuthenticationFailed('UnAuthorized')
        try:
            payload = jwt.decode(token, os.environ.get('ACCESS_TOKEN'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthorized')
        

        question = Assignment.objects.filter(id=id).first()
        serializer = AssignmentSerializer(question)
        numOfQuestion = len(serializer.data['question'])
        os.environ["OPENAI_API_KEY"] = os.environ.get('OPENAI_API_KEY')
        accuracy_criteria = {
            "accuracy": """
            Score 1: The answer is completely wrong.
            Score 3: The answer has minor relevance but does not align with the true answer.
            Score 5: The answer has moderate relevance but contains inaccuracies.
            Score 7: The answer aligns with the true answer but has minor errors or omission.
            Score 10: The answer is completely accurate and aligns perfectly with the reference."""
        }
        
        evaluator = load_evaluator(
            "labeled_score_string",
            criteria = accuracy_criteria,
            llm=ChatOpenAI(model="gpt-3.5-turbo-1106")
        )
        
        result = []
        reason = []
        for i in range(numOfQuestion):
            eval_result = evaluator.evaluate_strings(
                prediction=serializer.data['user_answer'][i],
                reference=serializer.data['answer'][i],
                input=serializer.data['question'][i]
            )
            result.append(eval_result['score'])
            reason.append(eval_result['reasoning'])
        
        data = {
            "result": result,
            "reason": reason
        }
        id = Assignment.objects.get(id=id)
        serializer = AssignmentSerializer(id, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response({
                "message": "Here is your result",
                "Result for each answer": serializer.data
            },
            status = status.HTTP_200_OK)
        else:
            return Response({
                "message": "error",
                "data": serializer.error_messages
            },
            status=status.HTTP_400_BAD_REQUEST)
          

class GetStudentCourses(APIView):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')[7:]
        
        if not token:
            raise AuthenticationFailed('UnAuthorized')
        try:
            payload = jwt.decode(token, os.environ.get('ACCESS_TOKEN'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthorized')
        
        role = payload['role']
        student_id = payload['id']
        connection = psycopg2.connect(database='qgae', user='qgae', password='quocviet01', host='localhost', port='5432')
        connection.autocommit = True
        cursor = connection.cursor()
        get_courses_id_query = '''SELECT course_id FROM api_student_courses WHERE "student_id" = %s'''
        get_courses_id = (student_id, )
        cursor.execute(get_courses_id_query, get_courses_id)
        courses_id = cursor.fetchall()
        
    
        joined_courses_id = list(itertools.chain.from_iterable(courses_id))
        
        courses_name = []
        for course_id in joined_courses_id:
            get_course_name_query = '''SELECT title, course_code FROM api_course WHERE "id" = %s'''
            get_course_name = (course_id, )
            cursor.execute(get_course_name_query, get_course_name)
            name = cursor.fetchone()
            get_course_assignments_id_query = '''SELECT assignment_id FROM api_assignment_courses WHERE "course_id" = %s'''
            get_course_assignment_id = (course_id, )
            cursor.execute(get_course_assignments_id_query, get_course_assignment_id)
            assignments_id = cursor.fetchall()
            joined_assignments_id = list(itertools.chain.from_iterable(assignments_id))
            get_lecturer_courses_id_query = '''SELECT api_student.id, api_student.fullname
                                                FROM  api_student 
                                                INNER JOIN api_student_courses 
                                                ON api_student_courses.student_id = api_student.id
                                                AND api_student_courses.course_id = %s AND api_student.role = %s '''
            get_lecturer_courses = (course_id, 'lecturer')
            cursor.execute(get_lecturer_courses_id_query, get_lecturer_courses)
            lecturer_id = cursor.fetchall()
            joined_lecturer_id = list(itertools.chain.from_iterable(lecturer_id))
            course_detail = {
                "id": course_id,
                "title": name[0],
                "course_code": name[1],
                "total_assignments": len(joined_assignments_id),
                "lecturer": joined_lecturer_id[1]
            }
            courses_name.append(course_detail)
        cursor.close()
        return Response(courses_name, status=status.HTTP_200_OK)
    
class GetProfile(APIView):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')[7:]
        
        if not token:
            raise AuthenticationFailed('UnAuthorized')
        try:
            payload = jwt.decode(token, os.environ.get('ACCESS_TOKEN'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthorized')
        
        user_id = payload['id']
        connection = psycopg2.connect(database='qgae', user='qgae', password='quocviet01', host='localhost', port='5432')
        connection.autocommit = True
        cursor = connection.cursor()
        get_profile_infor_query = '''SELECT * FROM api_student WHERE "id" = %s'''
        get_profile_infor = (user_id, )
        cursor.execute(get_profile_infor_query, get_profile_infor)
        user_infor = cursor.fetchone()
        user_information = {
            'id': user_infor[0],
            'student_id': user_infor[3],
            'fullname': user_infor[1],
            'role': user_infor[-1]
        }
        cursor.close()
        
        return Response(user_information, status=status.HTTP_200_OK)