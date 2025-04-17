from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {
                "code": status.HTTP_400_BAD_REQUEST,
                "reason": f"{exc}",
                "message": f"{exc}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Now add the HTTP status code to the response.
    if response is not None and response.data.get("@baseType") is not None:
        response.data["status_code"] = response.status_code
        response.data["code"] = response.status_code
        response.data["reason"] = response.data.get("reason", None)
        response.data["message"] = response.data.get("message", None)
        response.data["status"] = response.status_code
        return response

    return Response(
        {
            "code": status.HTTP_400_BAD_REQUEST,
            "reason": f"{exc}",
            "message": f"{exc}",
            "status": status.HTTP_400_BAD_REQUEST,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )
