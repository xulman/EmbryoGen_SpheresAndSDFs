# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import query_SDF_network_pb2 as query__SDF__network__pb2


class ClientToSDFStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.queryOne = channel.unary_unary(
                '/SDF_query_protocol.ClientToSDF/queryOne',
                request_serializer=query__SDF__network__pb2.QueryMsg.SerializeToString,
                response_deserializer=query__SDF__network__pb2.SDFvalue.FromString,
                )
        self.queryStream = channel.stream_stream(
                '/SDF_query_protocol.ClientToSDF/queryStream',
                request_serializer=query__SDF__network__pb2.QueryMsg.SerializeToString,
                response_deserializer=query__SDF__network__pb2.SDFvalue.FromString,
                )
        self.queryBox = channel.unary_unary(
                '/SDF_query_protocol.ClientToSDF/queryBox',
                request_serializer=query__SDF__network__pb2.QueryBox.SerializeToString,
                response_deserializer=query__SDF__network__pb2.SDFboxValues.FromString,
                )


class ClientToSDFServicer(object):
    """Missing associated documentation comment in .proto file."""

    def queryOne(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def queryStream(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def queryBox(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ClientToSDFServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'queryOne': grpc.unary_unary_rpc_method_handler(
                    servicer.queryOne,
                    request_deserializer=query__SDF__network__pb2.QueryMsg.FromString,
                    response_serializer=query__SDF__network__pb2.SDFvalue.SerializeToString,
            ),
            'queryStream': grpc.stream_stream_rpc_method_handler(
                    servicer.queryStream,
                    request_deserializer=query__SDF__network__pb2.QueryMsg.FromString,
                    response_serializer=query__SDF__network__pb2.SDFvalue.SerializeToString,
            ),
            'queryBox': grpc.unary_unary_rpc_method_handler(
                    servicer.queryBox,
                    request_deserializer=query__SDF__network__pb2.QueryBox.FromString,
                    response_serializer=query__SDF__network__pb2.SDFboxValues.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'SDF_query_protocol.ClientToSDF', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ClientToSDF(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def queryOne(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/SDF_query_protocol.ClientToSDF/queryOne',
            query__SDF__network__pb2.QueryMsg.SerializeToString,
            query__SDF__network__pb2.SDFvalue.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def queryStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/SDF_query_protocol.ClientToSDF/queryStream',
            query__SDF__network__pb2.QueryMsg.SerializeToString,
            query__SDF__network__pb2.SDFvalue.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def queryBox(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/SDF_query_protocol.ClientToSDF/queryBox',
            query__SDF__network__pb2.QueryBox.SerializeToString,
            query__SDF__network__pb2.SDFboxValues.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
