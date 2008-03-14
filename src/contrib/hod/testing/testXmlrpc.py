#Licensed to the Apache Software Foundation (ASF) under one
#or more contributor license agreements.  See the NOTICE file
#distributed with this work for additional information
#regarding copyright ownership.  The ASF licenses this file
#to you under the Apache License, Version 2.0 (the
#"License"); you may not use this file except in compliance
#with the License.  You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
import unittest, os, sys, re, threading, time

myDirectory    = os.path.realpath(sys.argv[0])
rootDirectory   = re.sub("/testing/.*", "", myDirectory)

sys.path.append(rootDirectory)

from hodlib.Common.xmlrpc import hodXRClient
from hodlib.Common.socketServers import hodXMLRPCServer

from testing.lib import BaseTestSuite

excludes = []

class test_HodXRClient(unittest.TestCase):
  def setUp(self):
    pass

  # All testMethods have to have their names start with 'test'
  def testSuccess(self):
    client = hodXRClient('http://localhost:5555', retryRequests=False)
    self.assertEqual(client.testing(), True)
    pass
    
  def testFailure(self):
    client = hodXRClient('http://localhost:5555', retryRequests=False)
    # client.noMethod()
    self.assertRaises(Exception, client.noMethod)
    pass

  def testTimeout(self):
    """HOD should raise Exception when rpc call times out"""
    client = hodXRClient('http://localhost:567823', retryRequests=False)
    # client.noMethod()
    self.assertRaises(Exception, client.testing)
    pass

  def testInterrupt(self):
    """ HOD should raise HodInterruptException when interrupted"""
    from hodlib.Common.util import hodInterrupt, HodInterruptException

    def interrupt():
      client = hodXRClient('http://localhost:59087')
      thread = threading.Thread(name='testinterrupt', target=client.testing)
      thread.start()
      time.sleep(1)
      hodInterrupt.setFlag()
      thread.join()

    self.assertRaises(HodInterruptException, interrupt)
    pass

  def tearDown(self):
    pass

class XmlrpcTestSuite(BaseTestSuite):
  def __init__(self):
    # suite setup
    BaseTestSuite.__init__(self, __name__, excludes)

    def rpcCall():
      return True
    
    self.server = hodXMLRPCServer('localhost', ['5555'])
    self.server.register_function(rpcCall, 'testing')
    self.thread = threading.Thread(name="server", 
                                   target=self.server._serve_forever)
    self.thread.start()
    time.sleep(1) # give some time to start server
  
  def cleanUp(self):
    # suite tearDown
    self.server.stop()
    self.thread.join()

def RunXmlrpcTests():
  # modulename_suite
  suite = XmlrpcTestSuite()
  testResult = suite.runTests()
  suite.cleanUp()
  return testResult

if __name__ == "__main__":
  RunXmlrpcTests()
