# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: schema.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cschema.proto\"\x1a\n\x07\x41irport\x12\x0f\n\x07\x61irport\x18\x02 \x01(\t\"|\n\nFlightData\x12\x0c\n\x04\x64\x61te\x18\x02 \x01(\t\x12\x1d\n\x0b\x66rom_flight\x18\r \x03(\x0b\x32\x08.Airport\x12\x1b\n\tto_flight\x18\x0e \x03(\x0b\x32\x08.Airport\x12\x16\n\tmax_stops\x18\x05 \x01(\x05H\x00\x88\x01\x01\x42\x0c\n\n_max_stops\"k\n\x04Info\x12\x19\n\x04\x64\x61ta\x18\x03 \x03(\x0b\x32\x0b.FlightData\x12\x13\n\x04seat\x18\t \x01(\x0e\x32\x05.Seat\x12\x1e\n\npassengers\x18\x08 \x03(\x0e\x32\n.Passenger\x12\x13\n\x04trip\x18\x13 \x01(\x0e\x32\x05.Trip*S\n\x04Seat\x12\x10\n\x0cUNKNOWN_SEAT\x10\x00\x12\x0b\n\x07\x45\x43ONOMY\x10\x01\x12\x13\n\x0fPREMIUM_ECONOMY\x10\x02\x12\x0c\n\x08\x42USINESS\x10\x03\x12\t\n\x05\x46IRST\x10\x04*E\n\x04Trip\x12\x10\n\x0cUNKNOWN_TRIP\x10\x00\x12\x0e\n\nROUND_TRIP\x10\x01\x12\x0b\n\x07ONE_WAY\x10\x02\x12\x0e\n\nMULTI_CITY\x10\x03*_\n\tPassenger\x12\x15\n\x11UNKNOWN_PASSENGER\x10\x00\x12\t\n\x05\x41\x44ULT\x10\x01\x12\t\n\x05\x43HILD\x10\x02\x12\x12\n\x0eINFANT_IN_SEAT\x10\x03\x12\x11\n\rINFANT_ON_LAP\x10\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'schema_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SEAT._serialized_start=279
  _SEAT._serialized_end=362
  _TRIP._serialized_start=364
  _TRIP._serialized_end=433
  _PASSENGER._serialized_start=435
  _PASSENGER._serialized_end=530
  _AIRPORT._serialized_start=16
  _AIRPORT._serialized_end=42
  _FLIGHTDATA._serialized_start=44
  _FLIGHTDATA._serialized_end=168
  _INFO._serialized_start=170
  _INFO._serialized_end=277
# @@protoc_insertion_point(module_scope)
