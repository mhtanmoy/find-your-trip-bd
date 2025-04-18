import json
import logging
from datetime import datetime


class LogFormatter(logging.Formatter):
    def format(self, record):
        place_holder = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        record.class_name = ""
        session_headers = {}
        if record.args and type(record.args) is dict:
            record.class_name = record.args.get("class_name", "")
            record.status_code = record.args.get("status_code", "")
            if "session_headers" in record.args:
                session_headers = record.args["session_headers"]
        log_headers = {}
        try:
            record.session_headers = json.dumps(log_headers).replace('"', "")

            record.date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        except Exception:
            record.session_headers = json.dumps(log_headers).replace('"', "")
            place_holder = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            record.date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        return super().format(record)


logger = logging.getLogger()

ch = logging.StreamHandler()
ch.setFormatter(
    LogFormatter("%(date_time)s %(pathname)s:%(lineno)s - %(message)s")  # noqa: E501
)

logging.basicConfig(level=logging.INFO, handlers=[ch])
