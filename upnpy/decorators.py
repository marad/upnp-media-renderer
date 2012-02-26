'''
Created on 25-02-2012

@author: morti
'''

from upnpy.device import Action as ServiceAction
from upnpy.device import StateVariable
from upnpy.device import ActionArgument
from upnpy.device import Service
from inspect import getmembers, getargspec

class ServiceInit(object):
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args, **kwargs):
        # Run base class constructor
        Service.__init__(self.obj)
        # Run user defined constructor
        self.func.__call__(self.obj, *args, **kwargs)
        
        # Check all attributes
        for k, v in getmembers(self.obj):
            if k.startswith("__"): continue
            
            # If they have attribute 'isAction' set to True
            if hasattr(v, 'isAction') and v.isAction:
                print 'Found action:', v
                
                # Begin creating action object
                functionArgList = getargspec(v).args
                functionArgumentCount = len(functionArgList) - 1 # without self
                
                argList = {}
                if hasattr(v, 'argList'):
                    if len(v.argList) < functionArgumentCount:
                        raise Exception("(%s, %s):Action in-arguments must match method arguments!" % (self.cls, v.__func__.__name__))                    
                    
                    for name, direction, rStV, kwargs in v.argList:
                        if name not in functionArgList and direction == ActionArgument.DIR_IN:
                            raise Exception("(%s, %s):Action in-arguments must match method arguments!" % (self.cls, v.__func__.__name__))
                        arg = ActionArgument(name=name,
                                             direction=direction,
                                             relatedStateVariable=rStV)
                                            
                        for key, value in zip(kwargs.keys(), kwargs.values()):
                            setattr(arg, key, value)
                            
                        if arg.relatedStateVariable != None:
                            if not arg.relatedStateVariable in self.obj.stateVariables.keys():
                                raise Exception("State variable '%s' doesn't exist!" % arg.relatedStateVariable)
                            else:
                                stv = self.obj.stateVariables[arg.relatedStateVariable]
                                arg.relatedStateVariableRef = stv
    
                        argList[name] = arg
                else:
                    if functionArgumentCount > 0:
                        raise Exception("(%s, %s):Action in-arguments must match method arguments!" % (self.cls, v.__func__.__name__))
                
                action = ServiceAction(name=v.__func__.__name__,
                                       argumentList=argList)
                self.obj.addAction(action)
    
    def __get__(self, obj, cls):
        self.obj = obj
        self.cls = cls
        return self.__call__    
    


def Action(func):
    func.isAction = True    
    return func
    
def Argument(name,
             direction,
             relatedStateVariable,
             **kwargs):
    def inner(func):
        if not hasattr(func, 'argList'):
            func.argList = []
        func.argList.append((name, direction, relatedStateVariable, kwargs))
        return func
    return inner


class MyService(Service):
    
    @ServiceInit
    def __init__(self):
        self.addStateVariable(
                StateVariable(
                        name='testVar',
                        dataType=StateVariable.TYPE_STRING))
        self.addStateVariable(descDict={ 
                'name'     : 'secVar',
                'dataType' : StateVariable.TYPE_INT,
                'allowedValueList' : [1, 3, 13]})
        
        
    @Action
    @Argument('arg1', 'in', 'testVar', other='info')
    @Argument('arg2', 'in', 'secVar')
    @Argument('shitOut', 'out', 'secVar')
    def myAction(self, arg1, arg2):
        print arg1, arg2
    
    @Action
    def notAction(self):
        pass

def log(x):
    print x    

def showProps(o, prefix=''):
    
    try:
        v = vars(o)
    except: 
        #log( prefix + repr(o) )
        if isinstance(o, list):
            #log (prefix+ '\t'+ o)
            for object in o:
                showProps(object, prefix=prefix + '\t\t')
        elif isinstance(o, dict):
            #log(prefix + k)
            for key, value in zip(o.keys(), o.values()):
                log(prefix + '\t' + key + ':')
                showProps(value, prefix=prefix + '\t\t')
        return
    
    for k, v in zip(v.keys(), v.values()):
        try:
            if isinstance(v, list):
                log (prefix + '\t' + k)
                for object in v:
                    showProps(object, prefix=prefix + '\t\t')
            elif isinstance(v, dict):
                log(prefix + k)
                for key, value in zip(v.keys(), v.values()):
                    log(prefix + '\t' + key + ':')
                    showProps(value, prefix=prefix + '\t\t')
            else:
                log(prefix + k + ' = ' + v)
        except Exception as e:
            #print e
            pass
        
def show(o, prefix=''):
    try:
        v = vars(o)
        for key, val in zip(v.keys(), v.values()):
            log(prefix + key)
            if val != None: show(val, prefix + '\t')
    except:
        if isinstance(o, list):
            #log (prefix+ '\t'+ o)
            for object in o:
                showProps(object, prefix=prefix + '\t\t')
        elif isinstance(o, dict):
            #log(prefix + k)
            for key, value in zip(o.keys(), o.values()):
                log(prefix + '\t' + key + ':')
                showProps(value, prefix=prefix + '\t\t')
        else:
            log(prefix + repr(o))
        
srv = MyService()
show(srv)

print srv.stateVariables['secVar'].allowedValueList

from lxml import etree
print etree.tostring(srv.genSCPD(), pretty_print=True)