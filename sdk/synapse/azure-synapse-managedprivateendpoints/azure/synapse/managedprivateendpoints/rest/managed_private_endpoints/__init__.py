# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

try:
    from ._request_builders_py3 import build_get_request
    from ._request_builders_py3 import build_create_request
    from ._request_builders_py3 import build_delete_request
    from ._request_builders_py3 import build_list_request
except (SyntaxError, ImportError):
    from ._request_builders import build_get_request  # type: ignore
    from ._request_builders import build_create_request  # type: ignore
    from ._request_builders import build_delete_request  # type: ignore
    from ._request_builders import build_list_request  # type: ignore

__all__ = [
    "build_get_request",
    "build_create_request",
    "build_delete_request",
    "build_list_request",
]
