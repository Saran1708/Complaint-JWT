from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate

from .serializers import UserSerializer,ComplaintSerializer
from .models import User,Complaint,Department

# Create your views here.
class ProxyUser(User):
    class Meta:
        proxy=True

    @property
    def is_authenticated(self):
        return True
    
class CustomJWTAuthentication(JWTAuthentication):   
    def get_user(self,validated_token):
        user_id = validated_token.get("user_id")
        try:
            return ProxyUser.objects.get(id=user_id)
        except ProxyUser.DoesNotExist:
            raise InvalidToken({'user not found'})
        


# def login(request):

#     email = request.data.get("email")
#     password = request.data.get("password")

#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return Response("Email Not Found", status=404)

#     # Django handles hashed password check
#     user = authenticate(username=user.username, password=password)

#     if user is None:
#         return Response("Invalid Password", status=400)

#     token = RefreshToken.for_user(user).access_token
  
#     return Response({"token": str(token)}, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])

def login(request):
    
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response("Invalid Email",status=status.HTTP_404_NOT_FOUND)
    
    if user.password != password:
        return Response("Invalid Password",status=status.HTTP_404_NOT_FOUND)
    
    # if not check_password(password, user.password):
    #     return Response({"msg": "Invalid Password"}, status=status.HTTP_404_NOT_FOUND)
    
    token = RefreshToken.for_user(user)

    return Response({"UserName":user.fullName,
                     "token":str(token.access_token)
                     },status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def getlist(request):

    stat = request.query_params.get("status","resolved")

    ans = Complaint.objects.filter(status=stat)
    serializer = ComplaintSerializer(ans,many=True)

    return Response (serializer.data,status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def add(request):

    user = request.user

    if user.dept is None or user.dept.deptName != "citizen" :
        return Response("You dont have permission",status=status.HTTP_403_FORBIDDEN)
    
   
 
    serializer= ComplaintSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    else:
        print(serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def update(request,id):

    user = request.user

    if user.dept is None or user.dept.deptName != "admin":
        return Response("You dont have permission",status=status.HTTP_403_FORBIDDEN)
    
    try:
        ans = Complaint.objects.get(id=id)
    except Complaint.DoesNotExist:
        return Response("Ticket Does Not Found",status=status.HTTP_404_NOT_FOUND)
    
    serializer = ComplaintSerializer(ans,data=request.data,partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomJWTAuthentication])
def delete(request,id):

    user = request.user

    try:
        ans = Complaint.objects.get(id=id)
    except Complaint.DoesNotExist:
        return Response("Ticket Does Not Found",status=status.HTTP_404_NOT_FOUND)
    
    if user.dept  and  user.dept.deptName == "admin":
        ans.delete()

        return Response("Deleted",status=status.HTTP_204_NO_CONTENT)

    if user.dept and user.dept.deptName == "citizen":
        if ans.user.id == user.id:
            ans.delete()

            return Response("Deleted",status=status.HTTP_204_NO_CONTENT)
        else:

            return Response("You dont have permission",status=status.HTTP_403_FORBIDDEN)

   
    
