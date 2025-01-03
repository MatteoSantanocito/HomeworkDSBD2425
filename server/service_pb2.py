# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: service.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rservice.proto\x12\x0cuser_service\"5\n\x10LoginUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x12\n\nrequest_id\x18\x02 \x01(\t\"5\n\x11LoginUserResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x0f\n\x07success\x18\x02 \x01(\x08\"o\n\x13RegisterUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x0e\n\x06ticker\x18\x02 \x01(\t\x12\x12\n\nrequest_id\x18\x03 \x01(\t\x12\x12\n\nhigh_value\x18\x04 \x01(\x01\x12\x11\n\tlow_value\x18\x05 \x01(\x01\"\'\n\x14RegisterUserResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"m\n\x11UpdateUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x0e\n\x06ticker\x18\x02 \x01(\t\x12\x12\n\nrequest_id\x18\x03 \x01(\t\x12\x12\n\nhigh_value\x18\x04 \x01(\x01\x12\x11\n\tlow_value\x18\x05 \x01(\x01\"%\n\x12UpdateUserResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"6\n\x11\x44\x65leteUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x12\n\nrequest_id\x18\x02 \x01(\t\"%\n\x12\x44\x65leteUserResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"&\n\x15GetLatestValueRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\"Y\n\x16GetLatestValueResponse\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x0e\n\x06ticker\x18\x02 \x01(\t\x12\r\n\x05value\x18\x03 \x01(\x01\x12\x11\n\ttimestamp\x18\x04 \x01(\t\"6\n\x16GetAverageValueRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\r\n\x05\x63ount\x18\x02 \x01(\x05\"O\n\x17GetAverageValueResponse\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x0e\n\x06ticker\x18\x02 \x01(\t\x12\x15\n\raverage_value\x18\x03 \x01(\x01\x32\xdb\x02\n\x12UserCommandService\x12U\n\x0cRegisterUser\x12!.user_service.RegisterUserRequest\x1a\".user_service.RegisterUserResponse\x12L\n\tLoginUser\x12\x1e.user_service.LoginUserRequest\x1a\x1f.user_service.LoginUserResponse\x12O\n\nUpdateUser\x12\x1f.user_service.UpdateUserRequest\x1a .user_service.UpdateUserResponse\x12O\n\nDeleteUser\x12\x1f.user_service.DeleteUserRequest\x1a .user_service.DeleteUserResponse2\xcf\x01\n\x10UserQueryService\x12[\n\x0eGetLatestValue\x12#.user_service.GetLatestValueRequest\x1a$.user_service.GetLatestValueResponse\x12^\n\x0fGetAverageValue\x12$.user_service.GetAverageValueRequest\x1a%.user_service.GetAverageValueResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_LOGINUSERREQUEST']._serialized_start=31
  _globals['_LOGINUSERREQUEST']._serialized_end=84
  _globals['_LOGINUSERRESPONSE']._serialized_start=86
  _globals['_LOGINUSERRESPONSE']._serialized_end=139
  _globals['_REGISTERUSERREQUEST']._serialized_start=141
  _globals['_REGISTERUSERREQUEST']._serialized_end=252
  _globals['_REGISTERUSERRESPONSE']._serialized_start=254
  _globals['_REGISTERUSERRESPONSE']._serialized_end=293
  _globals['_UPDATEUSERREQUEST']._serialized_start=295
  _globals['_UPDATEUSERREQUEST']._serialized_end=404
  _globals['_UPDATEUSERRESPONSE']._serialized_start=406
  _globals['_UPDATEUSERRESPONSE']._serialized_end=443
  _globals['_DELETEUSERREQUEST']._serialized_start=445
  _globals['_DELETEUSERREQUEST']._serialized_end=499
  _globals['_DELETEUSERRESPONSE']._serialized_start=501
  _globals['_DELETEUSERRESPONSE']._serialized_end=538
  _globals['_GETLATESTVALUEREQUEST']._serialized_start=540
  _globals['_GETLATESTVALUEREQUEST']._serialized_end=578
  _globals['_GETLATESTVALUERESPONSE']._serialized_start=580
  _globals['_GETLATESTVALUERESPONSE']._serialized_end=669
  _globals['_GETAVERAGEVALUEREQUEST']._serialized_start=671
  _globals['_GETAVERAGEVALUEREQUEST']._serialized_end=725
  _globals['_GETAVERAGEVALUERESPONSE']._serialized_start=727
  _globals['_GETAVERAGEVALUERESPONSE']._serialized_end=806
  _globals['_USERCOMMANDSERVICE']._serialized_start=809
  _globals['_USERCOMMANDSERVICE']._serialized_end=1156
  _globals['_USERQUERYSERVICE']._serialized_start=1159
  _globals['_USERQUERYSERVICE']._serialized_end=1366
# @@protoc_insertion_point(module_scope)
