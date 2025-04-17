from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


class ResponseWrapper(Response):

    def __init__(
        self,
        data=None,
        error_code=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
        error_message=None,
        message=None,
        response_success=True,
        status=None,
    ):

        if error_code is None and status is not None:
            if status > 299 or status < 200:
                error_code = status
                response_success = False
                data = data
        if error_code is not None:
            response_success = False

            data = {
                "code": error_code,
                "reason": error_message,
                "message": (
                    message
                    if message
                    else (
                        str(error_message)
                        if error_message
                        else "Success" if response_success else "Failed"
                    )
                ),
                "status": status,
            }

        super().__init__(
            data=data,
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )


class CustomRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]
        pagination = {"count": None, "next": None, "previous": None}
        if data:
            if "results" in data:
                try:
                    if data.get("results") is not None:
                        pagination["count"] = data.pop("count")
                        pagination["next"] = data.pop("next")
                        pagination["previous"] = data.pop("previous")
                        data = data.pop("results")
                    else:
                        error_code = 404
                        error_message = "No data found"
                        data = data.pop("results")
                except:
                    pass

        if response.status_code in [400, 401, 403, 404, 405, 409, 500]:
            error_code = response.status_code
            error_message = None
            if isinstance(data, dict):
                error_message = data.get("detail", None)
            elif isinstance(data, list):
                error_message = str(data)

            output_data = {
                "code": error_code,
                "reason": error_message,
                "message": response.status_text,
                "status": response.status_code,
            }
            return super().render(output_data, accepted_media_type, renderer_context)

        return super().render(data, accepted_media_type, renderer_context)
