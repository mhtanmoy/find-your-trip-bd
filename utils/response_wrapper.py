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
        is_error = error_code is not None or (
            status is not None and not (200 <= status <= 299)
        )

        if is_error:
            response_success = False
            data = {
                "code": error_code or status,
                "reason": error_message or "Error",
                "message": message or str(error_message) or "Failed",
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
        response = renderer_context.get("response", None)
        if not response:
            return super().render(data, accepted_media_type, renderer_context)

        status_code = response.status_code

        # Handle paginated responses
        if isinstance(data, dict) and "results" in data:
            pagination = {
                "count": data.pop("count", None),
                "next": data.pop("next", None),
                "previous": data.pop("previous", None),
            }
            results = data.pop("results", [])
            return super().render(
                {
                    "pagination": pagination,
                    "data": results,
                    "status": status_code,
                },
                accepted_media_type,
                renderer_context,
            )

        # Handle errors
        if status_code >= 400:
            error_message = None
            if isinstance(data, dict):
                error_message = data.get("detail") or data.get("message") or None
            elif isinstance(data, list):
                error_message = str(data)

            return super().render(
                {
                    "code": status_code,
                    "reason": error_message or "Something went wrong",
                    "message": response.status_text,
                    "status": status_code,
                },
                accepted_media_type,
                renderer_context,
            )

        # Success response
        return super().render(data, accepted_media_type, renderer_context)
