import os
from sys import platform

IS_WINDOWS = platform == 'win32'

class Constants:
  USE_UNIX_SOCKETS = False #not IS_WINDOWS
  ## Set the below three to the shared paths where
  ## the unix socket volume and data volume will be
  ## bind mounted with docker

  ## This only applies if using the UNIX socket transport
  ## for the API server
  DOCKER_UNIX_SOCKET_PATH = '/var/data/apiserver.sock'
  ## These two settings only apply if using the
  ## file based input parameters for the API server
  DOCKER_IMG_BASE_DIR = '/var/data/images'
  DOCKER_VID_BASE_DIR = '/var/data/videos'

  @staticmethod
  def getUnixSocketPath():
    return Constants.DOCKER_UNIX_SOCKET_PATH
  pass

  @staticmethod
  def getImageDir():
    return Constants.DOCKER_IMG_BASE_DIR
  pass

  @staticmethod
  def getVideoDir():
    return Constants.DOCKER_VID_BASE_DIR
  pass
pass

