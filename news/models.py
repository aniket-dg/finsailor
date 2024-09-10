from django.db import models

from datahub.models import Security


# Create your models here.
class StockEvent(models.Model):
    company = models.CharField(max_length=500)
    security = models.ForeignKey(
        Security,
        null=True,
        blank=True,
        related_name="events",
        on_delete=models.SET_NULL,
    )
    purpose = models.CharField(max_length=100)
    details = models.TextField(null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.company} - {self.purpose}"


# def post(self, request, item_type):
#     """
#     doc:
#         post:
#             description: This API creates categories and sub-categories
#             responses:
#                 code: [201, 400]
#                 message: ['Success', 'Fail']
#     """
#     try:
#         utility_id = request.data.get("remote_utility_id")
#         code = request.data.get("code")
#
#         if not utility_id or not code:
#             return Response(
#                 {"message": "Please provide a utility id and code."},
#                 status=HTTP_400_BAD_REQUEST,
#             )
#
#         serializer = CommonConfigSerializer(data=request.data)
#
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
#
#         key_list = code.split("_")
#         item_key = key_list[-1]
#
#         onboarding_config = OnboardingConfig.objects.filter(
#             remote_utility_id=utility_id
#         ).first()
#
#         if not onboarding_config:
#             return Response(
#                 {"message": "Bad request"},
#                 status=HTTP_400_BAD_REQUEST,
#             )
#
#         config_map = onboarding_config.config_map or {}
#         category_json = config_map.get("category_json", {})
#
#         # Function to recursively check for duplicate names
#         def check_duplicates(json_obj, name):
#             for key, value in json_obj.items():
#                 try:
#                     if value["_"]["name"].lower() == name.lower():
#                         return True
#                 except (KeyError, TypeError):
#                     pass
#                 if isinstance(value, dict):
#                     if check_duplicates(value, name):
#                         return True
#             return False
#
#         # Generate name based on code
#         if item_type != "category":
#             name = code.split("_")
#             parent_name = name[0]
#             name = name[1]
#             code = category_json[parent_name]["code"] + "_" + name
#             category_map = category_json[parent_name].pop('_', None)
#             revised_category_json = category_json[parent_name]
#         else:
#             name = code
#             revised_category_json = category_json
#             # Extract the highest number from existing codes
#             highest_number = 0
#             if category_json:
#                 highest_number = max(
#                     int(re.search(r"#(\d+)$", doc.get("code", "")).group(1))
#                     if re.search(r"#(\d+)$", doc.get("code", ""))
#                     else 0
#                     for doc in category_json.values()
#                 )
#
#             # Increment the number and generate a new code based on the name
#             code = f"{name}#{highest_number + 1}"
#
#         # Check for duplicate names in the entire JSON
#         if check_duplicates(revised_category_json, name):
#             return Response(
#                 {"message": f"Category/sub category with the name '{name}' already exists."},
#                 status=HTTP_400_BAD_REQUEST,
#             )
#         # # Create a new code for categories
#         if item_type != "category":
#             category_json[parent_name]['_'] = category_map
#
#         item_object = {
#             code: {
#                 "code": code,
#                 "_": {
#                     "name": name,
#                     "created_by": request.user["slug"],
#                     "created_date": str(datetime.datetime.now()),
#                     "utility_service": request.data.get("utility_service"),
#                     "active": True,
#                 },
#             }
#         }
#
#         # Update the nested dictionary structure
#         parent_map = category_json
#         for key in key_list[:-1]:
#             _object = parent_map.get(key)
#             if not _object:
#                 parent_map[key] = {"_": {}}
#                 _object = parent_map[key]
#             parent_map = _object
#
#         parent_map.update(item_object)
#         config_map["category_json"] = category_json
#
#         config_data = {"remote_utility_id": utility_id, "config_map": config_map}
#
#         serializer = ConfigSerializer(
#             onboarding_config, data=config_data, partial=True
#         )
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 status=HTTP_201_CREATED, data={"result": serializer.data}
#             )
#         return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
#
#     except Exception as e:
#         print(e)
#         logger.error("Category creation failed; Error: %s" % (str(e)))
#         raise CustomException(
#             message="Category creation failed",
#             status=HTTP_400_BAD_REQUEST,
#             log_msg=str(e),
#         )
