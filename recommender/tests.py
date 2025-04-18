# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.urls import reverse


# class TopDistrictViewSetTests(APITestCase):

#     def test_no_district_data_found(self):
#         url = reverse("top_districts-list")
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertIn("message", response.data)
#         self.assertEqual(
#             response.data["message"], "No district data found. Please try again."
#         )

#     def test_get_top_districts(self):
#         url = reverse("top_districts-list")
#         response = self.client.get(url)

#         self.assertIn(
#             response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
#         )


# class TravelRecommendationViewSetTests(APITestCase):

#     def test_success_response(self):
#         url = reverse("travel_recommendation-list")
#         response = self.client.get(
#             url,
#             {
#                 "lat": 23.685,
#                 "lon": 90.3563,
#                 "des_name": "Dhaka",
#                 "date": "2025-04-18",
#             },
#         )

#         self.assertIn(
#             response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
#         )

#     def test_missing_parameters(self):
#         url = reverse("travel_recommendation-list")
#         response = self.client.get(url, {"lat": 23.685, "lon": 90.3563})

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("message", response.data)

#     def test_invalid_parameters(self):
#         url = reverse("travel_recommendation-list")
#         response = self.client.get(url, {"lat": "invalid", "lon": "invalid"})

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("message", response.data)

#     def test_no_data_found(self):
#         url = reverse("travel_recommendation-list")
#         response = self.client.get(
#             url,
#             {
#                 "lat": 0.0,
#                 "lon": 0.0,
#                 "des_name": "Nowhere",
#                 "date": "2025-04-18",
#             },
#         )

#         self.assertIn(
#             response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]
#         )
