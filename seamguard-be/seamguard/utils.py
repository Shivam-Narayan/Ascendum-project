from rest_framework.response import Response

def success_response(message, data=None, status=200):
    return Response({
        "status": True,
        "message": message,
        "data": data
    }, status=status)

def error_response(error, status=400):
    return Response({
        "status": False,
        "message": error,
        "data": None
    }, status=status)
