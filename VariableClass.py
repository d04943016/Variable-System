#!/usr/bin/env python3
# Copyright (c) 2020 Wei-Kai Lee. All rights reserved

# coding=utf-8
# -*- coding: utf8 -*-



import sys, os, copy
from collections import OrderedDict, defaultdict
import numpy as np 

temptpath = os.path.dirname(os.path.abspath(__file__))
if temptpath not in sys.path:
    sys.path.append(temptpath)

class VariableClass:
    def __init__(self, valueDict, value=None):
        # _value_string == None : this object is not defined
        # _value_string is not stored in _valueDict : this object is a not defined variable
        self._valueDict = valueDict

        self._value = value
    # bool function
    def isEmpty(self):
        # return whether the stored variable is empty or not
        data = self.DataList
        if data is None:
            return True
        return len(data)==0
    def isVariable(self):
        # not defined in the variable dictionary
        if not isinstance(self._value, str):
            return False
        return (self._value not in self._valueDict)
    def delete(self):
        self._value = None
    @property 
    def DataList(self):
        # variable
        if isinstance(self._value, str) and (self._value not in self._valueDict):
            return None
        # in value dictionary
        if isinstance(self._value, str):
            return copy.deepcopy( self._valueDict[self._value] )
        # number list
        return copy.deepcopy( self._value )
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, new_value):
        # update _value
        self._value = new_value
    @property
    def value_string(self):
        if isinstance(self._value, str):
            return self._value
        return None
    def Number(self, calBool=True):
        if not calBool:
            return 1
        return len(self)
    # operator overloading
    def __getitem__(self, key):
        var = self.DataList
        return None if (var is None) else var[key]
    def __len__(self):
        var = self.DataList
        return 0 if (var is None) else len(var)
class VariableListClass(list):
    def __init__(self, valueDict, varList=None):
        list.__init__([])
        if varList is not None:
            for ii, var in enumerate( varList ):
                if isinstance(var, VariableClass):
                    self.append(var)
                else:
                    self.append( VariableClass(valueDict=valueDict, value=var) )
        self._valueDict = valueDict
    def Number(self, bool_list=None, skipNotDefined=False):
        # initialization
        bool_list = [True]*len(self) if (bool_list is None) else bool_list
        bool_list = np.array(bool_list)

        # variable name 
        VNList = np.array( self.VariableNameList )
        VNset  = np.array( self.VariableNameSet )
        VNsetIdxList = [ np.where(VNList==VN)[0] for VN in VNset]

        # calculate number
        number = 1
        for ii, VariableName in enumerate( VNset ):
            isCheck = len(VNsetIdxList[ii])!=0 and np.any( bool_list[VNsetIdxList[ii]] ) 
            # print(VariableName)
            if isCheck and (VariableName in self._valueDict): # is variable in valueDict
                # print('is variable in valueDict')
                number *= len( self._valueDict[ VariableName ] )
            elif isCheck and (VariableName is None): # number list
                # print('number list')
                for jj in VNsetIdxList[ii]:
                    # cprint(jj, bool_list[jj], self[jj].DataList, self[jj].Number(calBool=bool_list[jj]))
                    if bool_list[jj] and ( (self[jj].value is not None) or (not skipNotDefined) ):
                        number *= self[jj].Number(calBool=bool_list[jj])
            elif isCheck and (not skipNotDefined): # variable not in valueDict
                #print('variable not in valueDictc')
                return 0
        return number
    def Data(self, index, bool_list=None, NotDefinedValue=None):
        # initialization
        bool_list = [True]*len(self) if (bool_list is None) else bool_list
        bool_list = np.array(bool_list)

        # variable data list 
        tmp_valuedict = OrderedDict()
        validVNnumList = []
        for ii, var in enumerate(self):
            # vs: value string
            vs = var.value_string # value in/not in valueDict
            vs = vs if (vs is not None) else '__v{0}'.format(ii) # vii : number list
            #print(ii, var.value, vs)

            # add value into               tmp_valuedict      validVNnumList
            # number list            :       stored data                   N
            # value in valueDict     : data in valueDict                   N
            # value not in valueDict :                 X                   X (would not stord in tmp_valuedict)
            if (vs not in tmp_valuedict) and bool_list[ii] and ( (vs in self._valueDict) or (var.DataList is not None) ) :
                tmp_valuedict[vs] = var.DataList
                validVNnumList.append( var.Number(calBool=True) )

        #print(tmp_valuedict)
        #print(validVNnumList)

        # variable values
        valuesDict = OrderedDict()
        index2 = index
        for ii, key in enumerate( tmp_valuedict ):
            vList = tmp_valuedict[key]
            
            num = np.product( validVNnumList[ii+1::] ) if (ii+1!=len(validVNnumList)) else 1
            Vidx, index2 = (index2//num), (index2%num)
            valuesDict[key] = vList[Vidx]

        #print(valuesDict)

        # construct data
        results = [None] * len(self)

        # insert data
        for ii, var in enumerate(self):
            if not bool_list[ii]: # not loop variable
                results[ii] = var.DataList # number list/ in valueDict
                if results[ii] is None:    # not in valueDict
                    results[ii] = NotDefinedValue
            else: # loop value 
                vs = var.value_string 
                if vs is None: # number list
                    if self[ii].DataList is not None: 
                        results[ii] = valuesDict['__v{0}'.format(ii)] 
                    else: # intrinsic None
                        results[ii] = NotDefinedValue
                else: # value in/not in valueDict
                    if vs in valuesDict: # value in valueDict
                        results[ii] = valuesDict[vs]
                    else: # value not in valueDict
                        results[ii] = NotDefinedValue
        return results
    def isEmpty(self):
        return np.all( [ var.isEmpty() for var in self] ) or len(self)==0
    @property
    def DataList(self):
        return [ var.DataList for var in self ]
    @property
    def valueList(self):
        return [ var.value for var in self]
    @property
    def VariableNameList(self):
        return [ var.value_string for var in self ]
    @property
    def NumberList(self):
        return [ len(var) for var in self ]   
    @property
    def VariableNameSet(self):
        return list( OrderedDict.fromkeys( self.VariableNameList ) )
    # operator overloading
    def __getitem__(self, key):
        if isinstance(key, slice):
            return VariableListClass( valueDict=self._valueDict, varList=super().__getitem__(key) )
        return super().__getitem__(key)
    def __setitem__(self, key, value):
        if isinstance(key, slice):
            if isinstance(value, VariableListClass): 
                value = VariableListClass( valueDict=self._valueDict, varList=value )
        if not isinstance(value, VariableClass):
            value = VariableClass(valueDict=self._valueDict, value=value)
        super().__setitem__(key, value)
    def append(self, value):
        if not isinstance(value, VariableClass):
            value = VariableClass(valueDict=self._valueDict, value=value)
        super().append(value)
class VariableDictClass(dict):
    def __init__(self, valueDict, varDict):
        super().__init__()
        self._valueDict = valueDict
        for key in varDict:
            if isinstance(varDict[key], VariableListClass):
                self[key] = varDict[key]    
            else:
                self[key] = VariableListClass(valueDict=valueDict, varList=varDict[key])  
    def Number(self, bool_dict=None, skipNotDefined=False):
        bool_list = self._from_booldict_to_boollist(bool_dict=bool_dict)
        return self.VariableList.Number(bool_list=bool_list, skipNotDefined=skipNotDefined)
    def Data(self, index, bool_dict=None, NotDefinedValue=None):
        bool_list = self._from_booldict_to_boollist(bool_dict=bool_dict)
        data = self.VariableList.Data(index=index, bool_list=bool_list, NotDefinedValue=NotDefinedValue)

        datadict = defaultdict()
        idx = 0
        for key in self:
            mLen = len(self[key])
            datadict[key] = data[idx:idx+mLen]
            idx += mLen
        return datadict
    def _from_booldict_to_boollist(self, bool_dict=None):
        # initialization
        if bool_dict == None:
            bool_dict = defaultdict()

        bool_list = []
        for key in self:
            mlen = len(self[key])
            if key not in bool_dict:
                bool_list += [True]*mlen
            else:
                assert len(bool_dict[key])==len(self[key])
                bool_list += bool_dict[key]
        return bool_list
    def isEmpty(self):
        return self.VariableList.isEmpty()
    @property
    def VariableList(self):
        varList = VariableListClass(valueDict=self._valueDict)
        for key in self:
            varList += self[key]
        return varList
    @property
    def DataDict(self):
        VNDict = defaultdict()
        datalist = np.array( self.VariableList.DataList )
        
        idx = 0
        for key in self:
            mlen = len(self[key])
            VNDict[key] = datalist[idx:idx+mlen]
            idx = idx+mlen
        return VNDict    
    @property
    def valueDict(self):
        valueDict = defaultdict()
        valueList = np.array( self.VariableList.valueList )
        
        idx = 0
        for key in self:
            mlen = len(self[key])
            valueDict[key] = valueList[idx:idx+mlen]
            idx = idx+mlen
        return valueDict    
    @property
    def VariableNameDict(self):
        VNDict = defaultdict()
        VNname = np.array( self.VariableList.VariableNameList )
        
        idx = 0
        for key in self:
            mlen = len(self[key])
            VNDict[key] = VNname[idx:idx+mlen]
            idx = idx+mlen
        return VNDict
    @property
    def NumberDict(self):
        NDict = defaultdict()
        Nname = np.array( self.VariableList.NumberList )
        
        idx = 0
        for key in self:
            mlen = len(self[key])
            NDict[key] = Nname[idx:idx+mlen]
            idx = idx+mlen
        return NDict
    @property
    def VariableNameSetDict(self):
        NDict = defaultdict()
        VNset = np.array( self.VariableList.VariableNameSet )
        
        idx = 0
        for key in self:
            mlen = len(self[key])
            NDict[key] = VNset[idx:idx+mlen]
            idx = idx+mlen
        return NDict
if __name__ == '__main__':
    valueDict = { 'x':[0,1,2,3], 'y':[0.1,0.2,0.3], 'z':[10] }
    print(valueDict)
    print('-'*80)

    var1 = VariableClass(value=[0,0.1,0.2,0.3,0.4], valueDict=valueDict)
    print('var1.dataList     : ', var1.DataList)
    print('var1.isEmpty()    : ', var1.isEmpty())
    print('var1.isVariable() : ', var1.isVariable())
    print('var1.value        : ', var1.value)
    print('var1.value_string : ', var1.value_string)
    print('len(var1)         : ', len(var1))
    print('')
    print('change var1.value to ',[-0.1,-0.2,-0.3,-0.4])
    var1.value = [-0.1,-0.2,-0.3,-0.4]
    print('var1.dataList     : ', var1.DataList)
    print('var1.isEmpty()    : ', var1.isEmpty())
    print('var1.isVariable() : ', var1.isVariable())
    print('var1.value        : ', var1.value)
    print('var1.value_string : ', var1.value_string)
    print('len(var1)         : ', len(var1))
    print('valueDict         : ', valueDict)
    print('\n')


    print('-'*80)
    var2 = VariableClass(value=[], valueDict=valueDict)
    print('var2.dataList     : ', var2.DataList)
    print('var2.isEmpty()    : ', var2.isEmpty())
    print('var2.isVariable() : ', var2.isVariable())
    print('var2.value        : ', var2.value)
    print('var2.value_string : ', var2.value_string)
    print('len(var2)         : ', len(var2))
    print('')
    print('change var2.value to ','x')
    var2.value = 'x'
    print('var2.dataList     : ', var2.DataList)
    print('var2.isEmpty()    : ', var2.isEmpty())
    print('var2.isVariable() : ', var2.isVariable())
    print('var2.value        : ', var2.value)
    print('var2.value_string : ', var2.value_string)
    print('len(var2)         : ', len(var2))
    print('valueDict         : ', valueDict)
    print('\n')


    print('-'*80)
    var3 = VariableClass(value='A', valueDict=valueDict)
    print('var3.dataList     : ', var3.DataList)
    print('var3.isEmpty()    : ', var3.isEmpty())
    print('var3.isVariable() : ', var3.isVariable())
    print('var3.value        : ', var3.value)
    print('var3.value_string : ', var3.value_string)
    print('len(var3)         : ', len(var3))
    print('')
    print('change var3.value to ',None)
    var3.value = None
    print('var3.dataList     : ', var3.DataList)
    print('var3.isEmpty()    : ', var3.isEmpty())
    print('var3.isVariable() : ', var3.isVariable())
    print('var3.value        : ', var3.value)
    print('var3.value_string : ', var3.value_string)
    print('len(var3)         : ', len(var3))
    print('valueDict         : ', valueDict)
    print('\n')

    print('-'*80)
    var4 = VariableClass(value='A', valueDict=valueDict)
    print('var4.dataList     : ', var4.DataList)
    print('var4.isEmpty()    : ', var4.isEmpty())
    print('var4.isVariable() : ', var4.isVariable())
    print('var4.value        : ', var4.value)
    print('var4.value_string : ', var4.value_string)
    print('len(var4)         : ', len(var4))
    print('')


    print('-'*80)
    print('VariableListClass Test')
    VList = VariableListClass(valueDict=valueDict, varList=[var1, var2, var3, var4, var1, var2, var3, var4])
    print('VList.DataList               : ', VList.DataList)
    print('VList.VariableNameList       : ', VList.VariableNameList)
    print('VList.NumberList             : ', VList.NumberList)
    print('VList.Number                 : ', VList.Number() )
    print('VList.Number(TTFFTTFF)       : ', VList.Number( bool_list=[True, True, False, False, True, True, False, False] ) )
    print('VList.Number(TTTTTTTT) skip  : ', VList.Number( skipNotDefined=True ) )
    print('VList.Number(TFFFTFFF)       : ', VList.Number( bool_list=[True, False, False, False, True, False, False, False] ) )
    print('VList.Number(FTFFFTFF)       : ', VList.Number( bool_list=[False, True, False, False, False, True, False, False] ) )
    print('VList.Number(FFFFFFFF)       : ', VList.Number( bool_list=[False, False, False, False, False, False, False, False] ) )
    print('VList.Number(FFTFFFFF)       : ', VList.Number( bool_list=[False, False, True, False, False, False, False, False] ) )
    print('VList.Number(FFFTFFFF)       : ', VList.Number( bool_list=[False, False, False, True, False, False, False, False] ) )
    print('VList.Number(TTFFFFFF)       : ', VList.Number( bool_list=[True, True, False, False, False, False, False, False] ) )

    bool_list=[True, True, False, False, False, True, False, False]
    for ii in range( VList.Number(bool_list=bool_list, skipNotDefined=True) ):
        print('VList.Data({0})                : '.format(ii), VList.Data( index=ii, bool_list=bool_list, NotDefinedValue=True ) )
    print('\n')

    
    print('-'*80)
    print('VariableDictClass Test')
    varDict = {'Set1': [var1, var1], 'Set2':[var2,var3], 'Set3':[var1, var2, var3, var4] }
    VDict = VariableDictClass(valueDict=valueDict, varDict=varDict)
    print('NumberDict : ')
    print(VDict.NumberDict)
    print('valueDict : ')
    print(VDict.valueDict)
    print('DataDict : ')
    print(VDict.DataDict)
    print('VariableList : ')
    print(VDict.VariableList)
    print('VariableNameDict : ')
    print(VDict.VariableNameDict)
    print('Number : ', VDict.Number())
    print('Number : ', VDict.Number(skipNotDefined=True))

    bool_dict = {'Set1': [True, True], 'Set2':[False, False], 'Set3':[False, False, False, False] }
    for ii in range( VDict.Number(bool_dict=bool_dict, skipNotDefined=True) ):
        print('VDict.Data({0}) : '.format(ii), VDict.Data( index=ii, bool_dict=bool_dict, NotDefinedValue=-100 ) )















