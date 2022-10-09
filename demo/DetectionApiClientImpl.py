#!/usr/bin/env python

import sys
import pprint
import time
import traceback
import json
import os
import requests
from thrift.transport import TTransport, TSocket, TSSLSocket, THttpClient
from thrift.protocol.TBinaryProtocol import TBinaryProtocol

from api import DetectionApi
from api.ttypes import *
from constants import Constants

USE_UNIX_SOCK = Constants.USE_UNIX_SOCKETS
UNIX_SOCK_NAME = Constants.getUnixSocketPath()

pp = pprint.PrettyPrinter(indent=2)

class DetectionApiClient:
  @staticmethod
  def createClient(host='127.0.0.1', port=9090, uri='', framed=False,
                      ssl=False, validate=True, ca_certs=None, keyfile=None,
                      certfile=None, http=False, autoConnect=True):
    client = DetectionApiClient(host=host, port=port, uri=uri, framed=framed,
                ssl=ssl, validate=validate, ca_certs=ca_certs, keyfile=keyfile,
                certfile=certfile, http=http, autoConnect=autoConnect)
    return client
  pass

  @staticmethod
  def waitForServer(host='127.0.0.1', port=9090):
    while True:
      client = DetectionApiClient.createClient(host=host, port=port,
          autoConnect=False)
      try:
        client.connect()
      except Exception as e:
        print('Server connect failed, waiting...')
      isOpen = client.isOpen()
      print('Server status:', isOpen)
      if not isOpen:
        time.sleep(5)
      else:
        # clear all previous sessions
        sessions = client.getSessions()
        if len(sessions) > 0:
          print('Old sessions exist, deleting them now')
          for sess in sessions:
            client.deleteSession(sess.id)
        pass
        client.close()
        print('Server is up, returning')
        break
    pass
  pass

  def __init__(self, host='127.0.0.1', port=9090, uri='', framed=False,
                      ssl=False, validate=True, ca_certs=None, keyfile=None,
                      certfile=None, http=False, autoConnect=True):
    self.host = host
    self.port = port
    self.uri = uri
    self.framed = framed
    self.ssl = ssl
    self.validate = validate
    self.ca_certs = ca_certs
    self.keyfile = keyfile
    self.certfile = certfile
    self.http = http
    self.initTransport()
    if autoConnect:
      self.transport.open()
  pass

  def initTransport(self):
    if self.http:
      self.transport = THttpClient.THttpClient(self.host, self.port, self.uri)
    else:
      if self.ssl:
        socket = TSSLSocket.TSSLSocket(self.host, self.port, validate=self.validate,
                              ca_certs=self.ca_certs, keyfile=self.keyfile,
                              certfile=self.certfile)
      elif not USE_UNIX_SOCK:
        socket = TSocket.TSocket(self.host, self.port)
      else:
        socket = TSocket.TSocket(self.host, self.port, unix_socket=UNIX_SOCK_NAME)

      if self.framed:
        self.transport = TTransport.TFramedTransport(socket)
      else:
        self.transport = TTransport.TBufferedTransport(socket)
    pass
    protocol = TBinaryProtocol(self.transport)
    self.client = DetectionApi.Client(protocol)
  pass

  def connect(self):
    if self.transport is not None:
      self.transport.open()
  pass

  def isOpen(self):
    if self.transport is not None:
      return self.transport.isOpen()
    return False
  pass

  def reconnect(self):
    self.close()
    self.initTransport()
  pass

  def init(self, license):
    cmd = 'init'
    initReq = InitRequest(license=license)
    return self.runCommand(cmd, initReq=initReq)
  pass

  def getStatus(self):
    cmd = 'getStatus'
    return self.runCommand(cmd)
  pass

  def destroy(self):
    cmd = 'destroy'
    return self.runCommand(cmd)
  pass

  def createSession(self, detSettings):
    cmd = 'createSession'
    return self.runCommand(cmd, detSettings=detSettings)
  pass

  def getSessions(self):
    cmd = 'getSessions'
    return self.runCommand(cmd)
  pass

  def deleteSession(self, sessionId):
    cmd = 'deleteSession'
    return self.runCommand(cmd, sessionId=sessionId)
  pass

  def clearSession(self, sessionId):
    cmd = 'clearSession'
    return self.runCommand(cmd, sessionId=sessionId)
  pass

  def getSessionResult(self, sessionId):
    cmd = 'getSessionResult'
    return self.runCommand(cmd, sessionId=sessionId)
  pass

  def processInputForSession(self, sessionId, frameIndex, detInput):
    cmd = 'processInputForSession'
    return self.runCommand(cmd, sessionId=sessionId, frameIndex=frameIndex,
                                detInput=detInput)
  pass

  def runDetection(self, detInput, detSettings):
    cmd = 'runDetection'
    return self.runCommand(cmd, detInput=detInput, detSettings=detSettings)
  pass

  def runCommand(self, cmd, detSettings=None,
                       detInput=None, sessionId=-1,
                       frameIndex=0, initReq=None):
    try:
      if cmd == 'init':
        output = (self.client.init(initReq))
        #pp.pprint(output)
        return output

      elif cmd == 'getStatus':
        output = (self.client.getStatus())
        #pp.pprint(output)
        return output

      elif cmd == 'destroy':
        output = (self.client.destroy())
        #pp.pprint(output)
        return output

      elif cmd == 'createSession':
        output = (self.client.createSession(detSettings))
        #pp.pprint(output)
        return output

      elif cmd == 'getSessions':
        output = (self.client.getSessions())
        #pp.pprint(output)
        return output

      elif cmd == 'deleteSession':
        output = self.client.deleteSession(sessionId)
        #pp.pprint(output)
        return output

      elif cmd == 'clearSession':
        output = self.client.clearSession(sessionId)
        #pp.pprint(output)
        return output

      elif cmd == 'getSessionResult':
        output = self.client.getSessionResult(sessionId)
        #pp.pprint(output)
        return output

      elif cmd == 'processInputForSession':
        output = self.client.processInputForSession(sessionId, frameIndex, detInput)
        #pp.pprint(output)
        return output

      elif cmd == 'runDetection':
        output = self.client.runDetection(detInput, detSettings)
        #pp.pprint(output)
        return output
      else:
        print('Unrecognized method %s' % cmd)
        sys.exit(1)
    except Exception as e:
      print('api cmd failed with exception:', cmd, e)
      print(traceback.format_exc())
      ## reset transport in this case
      self.reconnect()
      ## send a generic err back to record it as failure
      return DetectionOutput(status=ResultCode.ERR_GENERIC)
    pass
  pass

  def close(self):
    if self.transport is not None:
      self.transport.close()
      self.transport = None
  pass
pass

