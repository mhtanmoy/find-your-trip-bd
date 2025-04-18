from rest_framework import serializers


class TopDistrictsSerializer(serializers.Serializer):
    page_size = serializers.IntegerField(
        required=False, default=10, help_text="Number of districts to return"
    )


class TravelQueryParamsSerializer(serializers.Serializer):
    lat = serializers.FloatField(
        required=True, help_text="Latitude of current location"
    )
    lon = serializers.FloatField(
        required=True, help_text="Longitude of current location"
    )
    name = serializers.CharField(required=True, help_text="Destination district name")
    date = serializers.DateField(required=True, help_text="Date in YYYY-MM-DD format")
