from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # 先呼叫 DRF 預設的 exception handler
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        # Validation Error (400)
        if response.status_code == 400:
            if isinstance(data, dict):
                # 只顯示第一個欄位的第一個錯誤
                first_key = next(iter(data))
                first_error = data[first_key]
                if isinstance(first_error, list):
                    message = first_error[0]
                else:
                    message = first_error
            elif isinstance(data, list):
                message = data[0] if data else "Invalid input."
            else:
                message = str(data)
            return Response({
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": message
                }
            }, status=400)
        # 其他已知錯誤（通常有 detail 欄位）
        elif isinstance(data, dict) and "detail" in data:
            message = data.get("detail", "")
            return Response({
                "success": False,
                "error": {
                    "code": f"HTTP_{response.status_code}",
                    "message": message
                }
            }, status=response.status_code)
        # 其他型別（如 list）
        else:
            message = str(data)
            return Response({
                "success": False,
                "error": {
                    "code": f"HTTP_{response.status_code}",
                    "message": message
                }
            }, status=response.status_code)
    # 完全未捕獲的例外
    return Response({
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": str(exc)
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 