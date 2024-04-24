from drf_yasg.inspectors import SwaggerAutoSchema


class CustomAutoSchema(SwaggerAutoSchema):

    def get_tags(self, operation_keys=None):
        """Get a list of tags for this operation. Tags determine how operations relate with each other, and in the UI
        each tag will show as a group containing the operations that use it. If not provided in overrides,
        tags will be inferred from the operation url. It will als check for the 'schema_tags' attr in the view class
        to add additional tags.

        :param tuple[str] operation_keys: an array of keys derived from the pathdescribing the hierarchical layout
            of this view in the API; e.g. ``('snippets', 'list')``, ``('snippets', 'retrieve')``, etc.
        :rtype: list[str]
        """

        operation_keys = operation_keys or self.operation_keys

        tags = self.overrides.get("tags")
        if not tags:
            if len(operation_keys) > 1:
                tags = [operation_keys[0], operation_keys[1]]
            else:
                tags = [operation_keys[0]]

        if getattr(self.view, "schema_tags", []):
            tags = tags + getattr(self.view, "schema_tags", [])

        return tags
