from pydantic import Field
from langserve import CustomUserType


# ATTENTION: Inherit from CustomUserType instead of BaseModel otherwise
#            the server will decode it into a dict instead of a pydantic model.
class FileProcessingRequest(CustomUserType):
    """Request including a base64 encoded file.


        Using with langchain tool
        -------------------------
        @tool(args_schema=FileProcessingRequest)
        def image_processor(image_data: str, operation: str) -> str:
            # Try to open if image data is a path to an image file
            try:
                with open(image_data, "rb") as img_file:
                    image_data = base64.b64encode(img_file.read()).decode('utf-8')
            except:
                # Assume image_data is already a base64 string
                # decode base64 image data and perform the specified operation
                decode_image = base64.b64decode(image_data)
            # Implementation logic here
            return f"Successfully performed {operation} on the provided image data."
            # Returning images
            ToolMessage(
                content=[
                    {
                        "type": "image",
                        "source_type": "base64",
                        "data": image_data,
                        "mime_type": "image/jpeg",
                    },
                ],
                tool_call_id="...",
            )

    """

    # The extra field is used to specify a widget for the playground UI.
    file: str = Field(..., json_schema_extra={"widget": {"type": "base64file"}})
    prompt: str = Field(..., json_schema_extra={"widget": {"type": "text"}})
