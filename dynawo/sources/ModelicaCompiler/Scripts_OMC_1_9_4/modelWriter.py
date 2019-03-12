#!/usr/bin/python

# -*- coding: utf-8 -*-

# Copyright (c) 2015-2019, RTE (http://www.rte-france.com)
# See AUTHORS.txt
# All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
# This file is part of Dynawo, an hybrid C++/Modelica open source time domain
# simulation tool for power systems.

import sys
import os

from utils import *
from headerPatternDefine import headerPatternDefine
from subprocess import Popen, PIPE
########################################################
#
#                  Writer Base
#
########################################################

##
# Writer Base
#
class modelWriterBase:
    ##
    # default constructor
    # @param self : object pointer
    # @param mod_name : model name to use when creating file
    def __init__(self,mod_name):
        ##  model name to use when creating file
        self.modName = mod_name
        ## data to print in cpp file
        self.fileContent = []
        ## data to print in header file
        self.fileContent_h = []
        ## data to print in header definition file
        self.fileContentDefinitions_h = []
        ## data to print header literals file
        self.fileContentLiterals_h = []

    ##
    # write cpp file
    # @param self : object pointer
    # @return
    def writeFile(self):
        write_file (self.fileContent, self.fileName)

    ##
    # write header file
    # @param self : object pointer
    # @return
    def writeHeaderFile(self):
        write_file (self.fileContent_h, self.fileName_h)


##
# Writer Manager
#
class modelWriterManager(modelWriterBase):
    ##
    # default constructor
    # @param self : object pointer
    # @param mod_name : name of the model
    # @param output_dir : directory where files should be writtern
    # @param init_pb : @b True if the model has an init model
    def __init__(self,mod_name,output_dir,init_pb):
        modelWriterBase.__init__(self,mod_name)
        ## name of the model to use in files
        self.className = mod_name
        ## canonical name of the cpp file
        self.fileName = os.path.join (output_dir, mod_name + ".cpp")
        ## canonical name of the header file
        self.fileName_h = os.path.join (output_dir, mod_name + ".h")
        ## indicates if the model has an init model
        self.hasInitPb = init_pb
        ## body of the cpp file
        self.body ="""
#include "__fill_model_name__.h"
#include "DYNSubModel.h"
__fill_model_include_header__

extern"C" DYN::SubModelFactory * getFactory()
{
  return (new DYN::Model__fill_model_name__Factory());
}

extern "C" DYN::SubModel * DYN::Model__fill_model_name__Factory::create() const
{
  DYN::SubModel * model (new DYN::Model__fill_model_name__() );
  return model;
}

namespace DYN {

Model__fill_model_name__::Model__fill_model_name__()
{
__fill_model_constructor__
}

Model__fill_model_name__::~Model__fill_model_name__()
{
__fill_model_destructor__
}

}

"""
        ## body of the header file
        self.bodyHeader="""
#ifndef __fill_model_name___h
#define __fill_model_name___h
#include "DYNModelManager.h"
#include "DYNSubModelFactory.h"

namespace DYN {

  class Model__fill_model_name__Factory : public SubModelFactory
  {
    public:
    Model__fill_model_name__Factory() {}
    ~Model__fill_model_name__Factory() {}

    SubModel * create() const;
  };

  class Model__fill_model_name__ : public ModelManager
  {
    public:
    Model__fill_model_name__();
    ~Model__fill_model_name__();

    bool hasInit() const { return __fill_has_init_model__; }
  };
}

#endif
"""
    ##
    # Defines the body of the cpp file (add new lines)
    # @param self : object pointer
    # @return
    def set_body(self):
        lines = self.body.split('\n')
        body = []
        for line in lines:
            body.append(line+'\n')

        for line in body:
            if "__fill_model_name__" in line:
                line_tmp = line.replace("__fill_model_name__",self.modName)
                self.fileContent.append(line_tmp)
            elif "__fill_model_include_header__" in line:
                self.fileContent.append("#include \""+ self.modName+"_Dyn.h\"\n")
                if self.hasInitPb:
                    self.fileContent.append("#include \""+ self.modName+"_Init.h\"\n")
            elif "__fill_model_constructor__" in line:
                self.fileContent.append("  modelType_ = std::string(\"" +self.modName +"\");\n")
                self.fileContent.append("  modelDyn_ = NULL;\n")
                self.fileContent.append("  modelInit_ = NULL;\n")
                self.fileContent.append("  modelDyn_ = new Model"+ self.modName+"_Dyn();\n")
                self.fileContent.append("  modelDyn_->setModelManager(this);\n")
                self.fileContent.append("  modelDyn_->setModelType(this->modelType());\n")
                if self.hasInitPb:
                    self.fileContent.append("  modelInit_ = new Model"+ self.modName+"_Init();\n")
                    self.fileContent.append("  modelInit_->setModelManager(this);\n")
                    self.fileContent.append("  modelInit_->setModelType(this->modelType());\n")
            elif "__fill_model_destructor__" in line:
                self.fileContent.append("  delete modelDyn_;\n")
                if self.hasInitPb:
                    self.fileContent.append("  delete modelInit_;\n")
            else:
                self.fileContent.append(line)

    ##
    # Defines the body of the header file (add new lines)
    # @param self : object pointer
    # @return
    def setBodyHeader(self):
        lines = self.bodyHeader.split('\n')
        body = []
        for line in lines:
            body.append(line+'\n')

        for line in body:
            if "__fill_model_name__" in line:
                line_tmp = line.replace("__fill_model_name__",self.modName)
                self.fileContent_h.append(line_tmp)
            elif "__fill_has_init_model__" in line:
                fill_string = "false"
                if self.hasInitPb:
                    fill_string = "true"
                line_tmp = line.replace("__fill_has_init_model__",fill_string)
                self.fileContent_h.append(line_tmp)
            else:
                self.fileContent_h.append(line)


##
# Writer
#
class modelWriter(modelWriterBase):
    ##
    # default constructor
    # @param obj_factory : builder associated to the writer
    # @param mod_name : name of the model
    # @param output_dir : output directory where files should be written
    # @param init_pb : indicates if the model is an init model
    def __init__(self, obj_factory, mod_name, output_dir, init_pb = False):
        modelWriterBase.__init__(self,mod_name)
        ## builder associated to the writer
        self.builder = obj_factory
        ## indicates if the model is an init model
        self.init_pb_ = init_pb
        ## define the name of the class to use in cpp/h files
        self.className =""
        if init_pb:
            self.className = mod_name + "_Init"
        else:
            self.className = mod_name + "_Dyn"

        ## Cpp file to generate
        self.fileName = os.path.join(output_dir, self.className + ".cpp")

        ## header file to generate
        self.fileName_h = os.path.join(output_dir, self.className + ".h")

        ## header file to generate
        self.fileNameLiterals_h = os.path.join(output_dir, self.className + "_literal.h")

        ## header file to generate
        self.fileNameDefinitions_h = os.path.join(output_dir, self.className + "_definition.h")

        ## filename for external functions
        self.fileName_external   = os.path.join(output_dir, self.className + "_external.cpp")

        ## List of external functions
        self.fileContent_external=[]
        ## data to print header literals file
        self.fileContentLiterals_h = []

    ##
    # Add an empty line in external file
    # @param self : object pointer
    # @return
    def addEmptyLine_external(self):
        self.fileContent_external.append("\n")

    ##
    # Add a line in external file
    # @param self : object pointer
    # @param line : line to add
    # @return
    def addLine_external(self, line):
        self.fileContent_external.append(line)

    ##
    # Add a list of lines in external file
    # @param self : object pointer
    # @param body : list of lines to add
    # @return
    def addBody_external(self, body):
        self.fileContent_external.extend(body)

    ##
    # Add empty line in file
    # @param self : object pointer
    # @return
    def addEmptyLine(self):
        self.fileContent.append("\n")

    ##
    # Add a line in file
    # @param self : object pointer
    # @param line : line to add
    # @return
    def addLine(self, line):
        self.fileContent.append(line)

    ##
    # Add a list of lines in file
    # @param self : object pointer
    # @param body : list of lines to add
    # @return
    def addBody(self, body):
        self.fileContent.extend(body)


    ##
    # define the head of the external file
    # @param self : object pointer
    # @return
    def getHeadExternalCalls(self):
        self.fileContent_external.append("#include <math.h>\n")
        self.fileContent_external.append("#include \"DYNModelManager.h\"\n") # DYN_assert overload
        if self.init_pb_:
            self.fileContent_external.append("#include \"" + self.modName + "_Init_literal.h\"\n")
        else:
            self.fileContent_external.append("#include \"" + self.modName + "_Dyn_literal.h\"\n")
        self.fileContent_external.append("#include \"" + self.className + ".h\"\n")
        self.fileContent_external.append("namespace DYN {\n")
        self.fileContent_external.append("\n")

    ##
    # define the head of the cpp file
    # @param self : object pointer
    # @return
    def getHead(self):
        self.fileContent.append("#include <limits>\n")
        self.fileContent.append("#include <cassert>\n")
        self.fileContent.append("#include <set>\n")
        self.fileContent.append("#include <string>\n")
        self.fileContent.append("#include <vector>\n")
        self.fileContent.append("#include <math.h>\n")
        self.fileContent.append("\n")
        self.fileContent.append("#include \"DYNElement.h\"\n")
        self.fileContent.append("\n")
        self.fileContent.append("#include \"" + self.className + ".h\"\n")
        if self.init_pb_:
            self.fileContent.append("#include \"" + self.modName + "_Init_definition.h\"\n")
            self.fileContent.append("#include \"" + self.modName + "_Init_literal.h\"\n")
        else:
            self.fileContent.append("#include \"" + self.modName + "_Dyn_definition.h\"\n")
            self.fileContent.append("#include \"" + self.modName + "_Dyn_literal.h\"\n")
        self.fileContent.append("\n")
        self.fileContent.append("\n")
        self.fileContent.append("namespace DYN {\n")
        self.fileContent.append("\n")

    ##
    # define the end of the cpp file
    # @param self : object pointer
    # @return
    def fill_tail(self):
        self.addEmptyLine()
        self.addLine("}")

    ##
    # define the end of the external file
    # @param self : object pointer
    # @return
    def fill_tailExternalCalls(self):
        self.addEmptyLine_external()
        self.addLine_external("}")


    ##
    # Add the body of setFomc in the cpp file
    # @param self : object pointer
    # @return
    def fill_setFomc(self):
        self.addEmptyLine()

        self.addLine("void Model" + self.className + "::setFomc(double * f)\n")
        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_setf())
        self.addLine("}\n")

    ##
    # Add the body of evalMode in the cpp file
    # @param self : object pointer
    # @return
    def fill_evalMode(self):
        self.addEmptyLine()

        self.addLine("bool Model" + self.className + "::evalMode(const double & t) const\n")
        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_evalmode())
        self.addLine("}\n")

    ##
    # Add the body of setZomc in the cpp file
    # @param self : object pointer
    # @return
    def fill_setZomc(self):
        self.addEmptyLine()

        self.addLine("void Model" + self.className + "::setZomc()\n")
        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_setz())
        self.addLine("}\n")

    ##
    # Add the body of setGomc in the cpp file
    # @param self : object pointer
    # @return
    def fill_setGomc(self):
        self.addEmptyLine()

        self.addLine("void Model" + self.className + "::setGomc(state_g * gout)\n")
        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_setg())
        self.addLine("}\n")


    ##
    # Add the body of setY0omc in the cpp file
    # @param self : object pointer
    # @return
    def fill_setY0omc(self):
        self.addEmptyLine()
        self.addLine("void Model" + self.className + "::setY0omc()\n")
        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_sety0())
        self.addLine("}\n")

    ##
    # Add the body of setVariables in the cpp file
    # @param self : object pointer
    # @return
    def fill_setVariables(self):
        self.addEmptyLine()
        self.addLine("void Model" + self.className + "::defineVariables(std::vector<boost::shared_ptr<Variable> >& variables)\n")
        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_setvariables())
        self.addLine("}\n")

    ##
    # Add the body of defineParameters in the cpp file
    # @param self : object pointer
    # @return
    def fill_defineParameters(self):
        self.addEmptyLine()
        self.addLine("void Model" + self.className + "::defineParameters(std::vector<ParameterModeler>& parameters)\n")
        self.addLine("{\n")
        self.addBody(self.builder.get_list_for_defineparameters())
        self.addLine("}\n")

    ##
    # Add the body of initRpar in the cpp file
    # @param self : object pointer
    # @return
    def fill_initRpar(self):
        self.addEmptyLine()
        self.addLine("void Model" + self.className + "::initRpar()\n")
        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_initrpar())

        self.addEmptyLine()
        self.addLine("  return;\n")
        self.addLine("}\n")

    ##
    # Add the body of setupDataStruc in the cpp file
    # @param self : object pointer
    # @return
    def fill_setupDataStruc(self):
        self.addEmptyLine()
        self.addLine("void Model" + self.className + "::setupDataStruc()\n")
        self.addLine("{\n")
        self.addEmptyLine()

        self.addBody(self.builder.get_setupdatastruc())

        self.addLine("  data->nbVars ="+str(len(self.builder.listVarsSyst))+";\n")
        self.addLine("  data->nbF = "+str(self.builder.get_nb_eq_dyn()) +";\n")
        self.addLine("  data->nbModes = 0; \n")
        self.addLine("  data->nbZ = "+str(len(self.builder.listAllVarsDiscr))+";\n")
        self.addLine("}\n")

    ##
    # Add the body of setYType_omc in the cpp file
    # @param self : object pointer
    # @return
    def fill_setYType_omc(self):
        self.addEmptyLine()
        if self.init_pb_ and len(self.builder.get_list_for_setytype()) == 0:
          self.addLine("void Model" + self.className + "::setYType_omc(propertyContinuousVar_t* /*yType*/)\n")
        else:
          self.addLine("void Model" + self.className + "::setYType_omc(propertyContinuousVar_t* yType)\n")

        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_setytype())

        self.addLine("}\n")

    ##
    # Add the body of setFType_omc in the cpp file
    # @param self : object pointer
    # @return
    def fill_setFType_omc(self):
        self.addEmptyLine()
        if self.init_pb_ and len(self.builder.get_list_for_setftype()) == 0:
          self.addLine("void Model" + self.className + "::setFType_omc(propertyF_t* /*fType*/)\n")
        else:
          self.addLine("void Model" + self.className + "::setFType_omc(propertyF_t* fType)\n")

        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_setftype())

        self.addLine("}\n")

    ##
    # Add the body of defineElements in the cpp file
    # @param self : object pointer
    # @return
    def fill_defineElements(self):
        self.addEmptyLine()
        if self.init_pb_ and len(self.builder.get_list_for_defelem()) == 0:
          self.addLine("void Model" + self.className + "::defineElements(std::vector<Element>& /*elements*/, std::map<std::string, int >& /*mapElement*/)\n")
        else:
          self.addLine("void Model" + self.className + "::defineElements(std::vector<Element>& elements, std::map<std::string, int >& mapElement)\n")
        self.addLine("{\n")

        self.addBody( self.builder.get_list_for_defelem() )
        self.addLine("}\n")

    ##
    # Add the body of setParameters in the cpp file
    # @param self : object pointer
    # @return
    def fill_setParameters(self):
        self.addEmptyLine()
        self.addLine("void Model" + self.className + "::setParameters( boost::shared_ptr<parameters::ParametersSet> params )\n")
        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_setparams())
        self.addLine("}\n")

    ##
    # Add the body of setInternalParameters in the cpp file
    # @param self : object pointer
    # @return
    def fill_setSharedParamsDefault(self):
        self.addEmptyLine()
        self.addLine("boost::shared_ptr<parameters::ParametersSet> Model" + self.className + "::setSharedParametersDefaultValues()\n")
        self.addLine("{\n")

        self.addBody(self.builder.get_list_for_setsharedparamsdefaultvalue())
        self.addLine("}\n")

    ##
    # Add the body of evalFAdept in the cpp file
    # @param self : object pointer
    # @return
    def fill_evalFAdept(self):
        self.addEmptyLine()
        self.addLine("#ifdef _ADEPT_\n")
        self.addLine("void Model" + self.className + "::evalFAdept(const std::vector<adept::adouble> & x,\n")
        self.addLine("                              const std::vector<adept::adouble> & xd,\n")
        self.addLine("                              std::vector<adept::adouble> & res)\n")
        self.addLine("{\n")

        self.addBody( self.builder.get_list_for_evalfadept() )

        self.addLine("}\n")
        self.addLine("#endif\n")

    ##
    # Add literal constants in .h file
    # @param self : object pointer
    # @return
    def fill_externalLiteralConstants(self):
        new_content_h = []
        for line in self.fileContentLiterals_h:
            if ("__insert_literals__") in line:
                new_content_h.extend (self.builder.get_list_for_literalconstants())
            else:
                new_content_h.append (line)
        self.fileContentLiterals_h = new_content_h


    ##
    # Add the body of externalCalls in the external file
    # @param self : object pointer
    # @return
    def fill_externalCalls(self):
        self.addEmptyLine_external()
        body = self.builder.get_list_for_externalcalls()
        body_tmp=[]
        for line in body:
            if "__fill_model_name__" in line:
                line = line.replace("__fill_model_name__", "Model" + self.className)
            body_tmp.append(line)
        self.addBody_external(body_tmp)

    ##
    # Add the body of initData in the cpp file
    # @param self : object pointer
    # @return
    def fill_initData(self):
        self.addEmptyLine()
        self.addLine("void Model"+self.className +"::initData(DYNDATA *d)\n")
        self.addLine("{\n")
        self.addLine("  setData(d);\n")
        self.addLine("  setupDataStruc();\n")
        self.addLine("  initializeDataStruc();\n")
        self.addLine("}\n")

    ##
    # Add the body of deInitializeDataStruc in the cpp file
    # @param self : object pointer
    # @return
    def fill_deInitializeDataStruc(self):
        self.addEmptyLine()
        self.addLine("void Model"+ self.className +"::deInitializeDataStruc()\n")
        self.addLine("{\n")

        self.addBody( self.builder.get_list_for_deinitializedatastruc() )

        self.addLine("}\n")

    ##
    # Add the body of initializeDataStruc in the cpp file
    # @param self : object pointer
    # @return
    def fill_initializeDataStruc(self):
        self.addEmptyLine()
        self.addLine("void Model"+ self.className +"::initializeDataStruc()\n")
        self.addLine("{\n")

        self.addBody( self.builder.get_list_for_initializedatastruc() )

        self.addLine("}\n")

    ##
    # Add the body of checkDataCoherence in the cpp file
    # @param self : object pointer
    # @return
    def fill_warnings(self):
        self.addEmptyLine()
        self.addLine("void Model"+ self.className +"::checkDataCoherence()\n")
        self.addLine("{\n")

        self.addBody( self.builder.get_list_for_warnings() )

        self.addLine("}\n")

    ##
    # Add the body of setFequations in the cpp file
    # @param self : object pointer
    # @return
    def fill_setFequations(self):
        self.addEmptyLine()
        self.addLine("void Model"+ self.className +"::setFequations(std::map<int,std::string>& fEquationIndex)\n")
        self.addLine("{\n")
        self.addBody("  //Note: fictive equations are not added. fEquationIndex.size() = sizeF() - Nunmber of fictive equations.\n")
        self.addBody( self.builder.get_list_for_setf_equations() )
        self.addLine("}\n")

    ##
    # Add the body of setGequations in the cpp file
    # @param self : object pointer
    # @return
    def fill_setGequations(self):
        self.addEmptyLine()
        self.addLine("void Model"+ self.className +"::setGequations(std::map<int,std::string>& gEquationIndex)\n")
        self.addLine("{\n")
        self.addBody( self.builder.get_list_for_setg_equations() )
        self.addLine("}\n")

    ##
    # Define the header file
    # @param self : object pointer
    # @return
    def getHeaderPattern(self, additional_header_files):
        headerPattern = headerPatternDefine(additional_header_files)
        lines =[]
        if self.init_pb_:
            lines = headerPattern.get_init().split('\n')
        else:
            lines = headerPattern.get_dyn().split('\n')

        for line in lines:
            self.fileContent_h.append(line + '\n')

        if self.init_pb_:
            lines = headerPattern.get_init_literals().split('\n')
        else:
            lines = headerPattern.get_dyn_literals().split('\n')

        for line in lines:
            self.fileContentLiterals_h.append(line + '\n')

        if self.init_pb_:
            lines = headerPattern.get_init_definitions().split('\n')
        else:
            lines = headerPattern.get_dyn_definitions().split('\n')

        for line in lines:
            self.fileContentDefinitions_h.append(line + '\n')

    ##
    # Insert a checkSum to identify the model in header file
    # @param self : object pointer
    # @param input_dir : input directory where the cpp file is created
    # @return
    def insert_checkSum(self,input_dir):
        file_name = os.path.join (input_dir, self.className + ".cpp")
        md5sum_pipe = Popen(["md5sum",file_name],stdout = PIPE)
        check_sum = md5sum_pipe.communicate()[0].split()[0]

        content_h_tmp = []
        for n, line in enumerate(self.fileContent_h):
            if "__fill_model_checkSum__" in line:
                line_tmp = line.replace("__fill_model_checkSum__", check_sum)
                self.fileContent_h [n] = line_tmp

    ##
    # Insert the model name in header file
    # @param self : object pointer
    # @return
    def insert_model_name(self):
        for n, line in enumerate(self.fileContent_h):
            if "__fill_model_name__" in line:
                line_tmp = line.replace("__fill_model_name__", self.modName)
                self.fileContent_h [n] = line_tmp

    ##
    # Insert variables definitions
    # @param self: object pointer
    # @return NONE (act on self variable)
    def fill_variables_definitions(self):
        for n, line in enumerate(self.fileContentDefinitions_h):
            if "__fill_model_name__" in line:
                line_tmp = line.replace("__fill_model_name__", self.modName)
                self.fileContentDefinitions_h [n] = line_tmp

            elif "__fill_variables_definitions__h" in line:
                self.fileContentDefinitions_h [n : n+1] = self.builder.get_list_definitions_for_h()
                break

    ##
    # Insert external calls in header file
    # @param self : object pointer
    # @return
    def addExternalCalls(self):

        for n, line in enumerate(self.fileContent_h):
            if "__fill_internal_functions__" in line:
                file_content_tmp = []
                if len(self.builder.get_list_for_externalcalls_header())> 0 :
                    file_content_tmp.append("   //External Calls\n")
                    for line in self.builder.get_list_for_externalcalls_header():
                        file_content_tmp.append("     "+line)
                    file_content_tmp.append("\n")
                else:
                    file_content_tmp.append("   // No External Calls\n")

                self.fileContent_h [n : n+1] = file_content_tmp

    ##
    # Add the definition of parameters in header file
    # @param self : object pointer
    # @return
    def addParameters(self):
        for n, line in enumerate(self.fileContent_h):
            if "__insert_params__" in line:
                file_content_tmp = []
                file_content_tmp.append("      // Non-internal parameters \n")
                parameters_real = self.builder.get_list_params_real_not_internal_for_h()
                parameters_bool = self.builder.get_list_params_bool_not_internal_for_h()
                parameters_int = self.builder.get_list_params_integer_not_internal_for_h()
                parameters_string = self.builder.get_list_params_string_not_internal_for_h()
                for par in parameters_real + parameters_bool + parameters_int + parameters_string:
                    variable_type = par.get_value_type_modelica_c_code()
                    if (variable_type == "string"):
                        variable_type = "std::string"

                    file_content_tmp.append("      " + variable_type + " " + to_compile_name(par.get_name() + "_") + ";\n")

                self.fileContent_h [n : n+1] = file_content_tmp

    ##
    # write the external functions file
    # @param self : object pointer
    # @return
    def writeExternalCallsFile(self):
        write_file (self.fileContent_external, self.fileName_external)

    ##
    # write header literals file
    # @param self : object pointer
    # @return
    def writeHeaderLiteralsFile(self):
        write_file (self.fileContentLiterals_h, self.fileNameLiterals_h)


    ##
    # write header definitions file
    # @param self : object pointer
    # @return
    def writeHeaderDefinitionsFile(self):
        write_file (self.fileContentDefinitions_h, self.fileNameDefinitions_h)
