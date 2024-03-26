from jinja2 import Environment, FileSystemLoader
from json import loads
from pathlib import Path
from setup_data_to_json import SetupToJson
from dump_spirit_component import SpiritComponentDump
import xml.etree.ElementTree as ET
from io import StringIO

from xml.dom import minidom
from xml.dom.minidom import Node

import pyxb
from spirit_1685_2009 import binding
from pyxb.binding.facets import CF_enumeration

import click

class SetupToSpiritComponent:

    def generate(self, setup_py_file_path='test/setup.py', component_axilite_template_path = 'test/component_axilite_template.xml', component_xml_file_path='test/component.xml'):
        
        # --------------------------
        # extract data from setup.py
        # --------------------------
        extractor = SetupToJson()
        file_path = open(setup_py_file_path, 'r')     
        print("reading {}".format(setup_py_file_path))
        json_string = extractor.extract(setup_py_file_path)
        static_setup_data = loads(json_string)
        
        # -------------------------------------
        # prepare spirit template file
        # -------------------------------------        
        xml_template_file = open(component_axilite_template_path, 'r')
        xml_template_string = xml_template_file.read()
        xml_template_file.close()
        namespaces = dict([
             node for _, node in ET.iterparse(
                 StringIO(xml_template_string), events=['start-ns']
             )
        ])        
        
        for name, value in namespaces.items():
            ET.register_namespace(name, value)
        
        tree = ET.ElementTree(ET.fromstring(xml_template_string))
        root = tree.getroot()
        vendorExtensions = root.find("spirit:vendorExtensions", namespaces)
        vendorExtensions_parent = root.find(".", namespaces)
        vendorExtensions_parent.remove(vendorExtensions)
              
        spirit_xml_template_string = ET.tostring(root, encoding='utf8').decode('utf8')
        #dumper = SpiritComponentDump()
        #dumper.dump(spirit_xml_template_string)
        
        # -------------------------------------
        # extract data from top_hdl_entity_file
        # -------------------------------------    
        top_hdl_entity_file_path = static_setup_data["top_entity_file"] 
           
        print("reading {}".format(top_hdl_entity_file_path))
        top_hdl_entity_file = open(top_hdl_entity_file_path, 'r')
        top_hdl_entity_lines = top_hdl_entity_file.readlines()
        top_hdl_entity_file.close()
        
        top_hdl_entity_wo_comments = ""
        for l in top_hdl_entity_lines:
            if '--' in l:
                nl = l.split()[0]
                top_hdl_entity_wo_comments += nl
            else:
                top_hdl_entity_wo_comments += l
        
        vhdl = top_hdl_entity_wo_comments.split(';')
        vhdl_particles = []
        p = ""
        for t in vhdl:
            for e in t.split():
                p = p + e.strip() + ' '
            p = p.strip() + ';'                
            vhdl_particles.append(p)
            p=""
        
        entity = "" 
        in_entity = False   
        for p in vhdl_particles:
            if p.startswith('entity'):               
                in_entity = True
            if in_entity: 
                entity = entity + p + ' '
                if p.startswith('end'):
                    break
        
        entity = entity.strip()
        
        entity_particles = entity.split(';')
        
        entity_prefix = entity_particles[0].split('(')[0]
        entity_name = entity_prefix.split()[1]
        entity_ports = []
        entity_ports.append(entity_particles[0].split('(')[1].strip())
        for i, p in enumerate(entity_particles):
            if i == 0:
                continue
            if i == len(entity_particles) - 3:
                entity_ports.append(p[:-1].strip())
                continue       
            if i == len(entity_particles) - 2:
                continue
            if i == len(entity_particles) - 1:
                continue
            entity_ports.append(p.strip())
        
        entity_port_name_type_dict = {}
        
        for p in entity_ports:
            port_name = p.split(':')[0].strip()
            port_type = p.split(':')[1].strip()
            entity_port_name_type_dict[port_name] = port_type
        
        axilite_port_names = [
            "S_AXI_ACLK",
            "S_AXI_ARESETN",
            "S_AXI_AWVALID",
            "S_AXI_AWADDR",
            "S_AXI_AWPROT",
            "S_AXI_WVALID",
            "S_AXI_WDATA",
            "S_AXI_WSTRB",
            "S_AXI_BREADY",
            "S_AXI_ARVALID",
            "S_AXI_ARADDR",
            "S_AXI_ARPROT",
            "S_AXI_RREADY",
            "S_AXI_AWREADY",
            "S_AXI_WREADY",
            "S_AXI_BVALID",
            "S_AXI_BRESP",
            "S_AXI_ARREADY",
            "S_AXI_RVALID",
            "S_AXI_RDATA",
            "S_AXI_RRESP",
            "Trace_Axi4LiteDown_AWVALID",
            "Trace_Axi4LiteDown_AWADDR",
            "Trace_Axi4LiteDown_AWPROT",
            "Trace_Axi4LiteDown_WVALID",
            "Trace_Axi4LiteDown_WDATA",
            "Trace_Axi4LiteDown_WSTRB",
            "Trace_Axi4LiteDown_BREADY",
            "Trace_Axi4LiteDown_ARVALID",
            "Trace_Axi4LiteDown_ARADDR",
            "Trace_Axi4LiteDown_ARPROT",
            "Trace_Axi4LiteDown_RREADY",
            "Trace_Axi4LiteUp_AWREADY",
            "Trace_Axi4LiteUp_WREADY",
            "Trace_Axi4LiteUp_BVALID",
            "Trace_Axi4LiteUp_BRESP",
            "Trace_Axi4LiteUp_ARREADY",
            "Trace_Axi4LiteUp_RVALID",
            "Trace_Axi4LiteUp_RDATA",
            "Trace_Axi4LiteUp_RRESP",
            "Trace_Axi4LiteAccess_WritePrivileged",
            "Trace_Axi4LiteAccess_WriteSecure",
            "Trace_Axi4LiteAccess_WriteInstruction",
            "Trace_Axi4LiteAccess_ReadPrivileged",
            "Trace_Axi4LiteAccess_ReadSecure",
            "Trace_Axi4LiteAccess_ReadInstruction",
            "Trace_UnoccupiedAck",
            "Trace_TimeoutAck" ]
        
        for n in axilite_port_names:
            del entity_port_name_type_dict[n]  
            
        # -------------------------------------
        # modify template in RAM
        # -------------------------------------                  
        try:
            component = binding.CreateFromDocument(spirit_xml_template_string)
        except pyxb.ValidationError as e:
            print(e.details())
            
        component.name = static_setup_data["top_entity"]
        component.description = static_setup_data["top_entity"] + "_v1_0"
                    
        for pn in entity_port_name_type_dict.items():     
            vhdlPortName = pn[0]
            vhdlPortType = pn[1]
            vhdlPortDirection = vhdlPortType.split()[0].strip()
            port = binding.port()
            port.name = vhdlPortName
            wire = binding.portWireType()
            wire.direction = binding.componentPortDirectionType(vhdlPortDirection)
            wireTypeDefs = binding.wireTypeDefs()
            wireTypeDef = binding.wireTypeDef()
            if "std_logic_vector" in vhdlPortType:
                vhdlPortTypeRange = vhdlPortType.split("(")[1].split(")")[0]
                vhdlPortTypeRangeLeft = vhdlPortTypeRange.split()[0].strip()
                vhdlPortTypeRangeRight = vhdlPortTypeRange.split()[2].strip()
                vector = binding.vector()
                vector.left = vhdlPortTypeRangeLeft 
                vector.left.format = binding.formatType("long")
                vector.right= vhdlPortTypeRangeRight 
                vector.right.format = binding.formatType("long")
                wire.vector = vector
                wireTypeDef.typeName = "std_logic_vector"
            else:
                wireTypeDef.typeName = "std_logic"
            wireTypeDef.viewNameRef.append("xilinx_anylanguagesynthesis")
            wireTypeDef.viewNameRef.append("xilinx_anylanguagebehavioralsimulation")
            wireTypeDefs.append(wireTypeDef)
            wire.wireTypeDefs = wireTypeDefs
            port.wire = wire
            component.model.ports.port.append(port)
            
        for _fileSetIdx, fileSet in enumerate(component.fileSets.fileSet):           
            if  fileSet.name == 'xilinx_anylanguagesynthesis_view_fileset':
                fileSet.file.clear()
                for fileBundle in static_setup_data["src_data_files"]: 
                    for fileElement in fileBundle[1]:          
                        if not "IP-XACT" in fileElement["file_type"]:       
                            file = binding.file()
                            file.name = "../" + fileElement["file"]                      
                            if "VHDL 2008" in fileElement["file_type"]:           
                                file.userFileType.append("vhdlSource-2008")
                            elif "VHDL" in fileElement["file_type"]:           
                                file.userFileType.append("vhdlSource")
                            elif "Verilog" in fileElement["file_type"]:     
                                file.userFileType.append("verilogSource")      
                            file.logicalName = "xil_defaultlib"   
                            fileSet.file.append(file)
            if fileSet.name == 'xilinx_anylanguagebehavioralsimulation_view_fileset':        
                fileSet.file.clear()
                for fileBundle in static_setup_data["src_data_files"]: 
                    for fileElement in fileBundle[1]:             
                        if not "IP-XACT" in fileElement["file_type"]:       
                            file = binding.file()
                            file.name = "../" + fileElement["file"]                      
                            if "VHDL 2008" in fileElement["file_type"]:           
                                file.userFileType.append("vhdlSource-2008")
                            elif "VHDL" in fileElement["file_type"]:           
                                file.userFileType.append("vhdlSource")
                            elif "Verilog" in fileElement["file_type"]:     
                                file.userFileType.append("verilogSource")      
                            file.logicalName = "xil_defaultlib"   
                            fileSet.file.append(file)
                for fileBundle in static_setup_data["tb_data_files"]: 
                    for fileElement in fileBundle[1]:                
                        file = binding.file()
                        file.name = "../" + fileElement["file"]
                        if "VHDL 2008" in fileElement["file_type"]:           
                            file.userFileType.append("vhdlSource-2008")
                        elif "VHDL" in fileElement["file_type"]:           
                            file.userFileType.append("vhdlSource")
                        elif "Verilog" in fileElement["file_type"]:     
                            file.userFileType.append("verilogSource")     
                        file.userFileType.append("USED_IN_ipstatic")                    
                        file.logicalName = "xil_defaultlib"                    
                        fileSet.file.append(file)  
            if fileSet.name == 'xilinx_testbench_view_fileset':
                fileSet.file.clear()        
                for fileBundle in static_setup_data["src_data_files"]: 
                    for fileElement in fileBundle[1]:             
                        if not "IP-XACT" in fileElement["file_type"]:       
                            file = binding.file()
                            file.name = "../" + fileElement["file"]                      
                            if "VHDL 2008" in fileElement["file_type"]:           
                                file.userFileType.append("vhdlSource-2008")
                            elif "VHDL" in fileElement["file_type"]:           
                                file.userFileType.append("vhdlSource")
                            elif "Verilog" in fileElement["file_type"]:     
                                file.userFileType.append("verilogSource")      
                            file.logicalName = "xil_defaultlib"   
                            fileSet.file.append(file)
                for fileBundle in static_setup_data["tb_data_files"]: 
                    for fileElement in fileBundle[1]:                
                        file = binding.file()
                        file.name = "../" + fileElement["file"]
                        if "VHDL 2008" in fileElement["file_type"]:           
                            file.userFileType.append("vhdlSource-2008")
                        elif "VHDL" in fileElement["file_type"]:           
                            file.userFileType.append("vhdlSource")
                        elif "Verilog" in fileElement["file_type"]:     
                            file.userFileType.append("verilogSource")     
                        file.userFileType.append("USED_IN_ipstatic")                    
                        file.logicalName = "xil_defaultlib"                    
                        fileSet.file.append(file)  
            if fileSet.name == 'xilinx_xpgui_view_fileset':
                fileSet.file.clear()          
                file = binding.file()
                file.name = "xgui/" + static_setup_data["top_entity"] + "_v1_0" + ".tcl"
                file.userFileType.append("CHECKSUM_f92e9879")
                file.userFileType.append("XGUI_VERSION_2")
                fileSet.file.append(file)       
                
        for _viewIdx, view in enumerate(component.model.views.view):           
            if view.name == 'xilinx_anylanguagesynthesis':  
                view.modelName = static_setup_data["top_entity"] 
                view.parameters.parameter.clear()          
            if view.name == 'xilinx_anylanguagebehavioralsimulation':  
                view.modelName = static_setup_data["tb_top_entity"] 
                view.parameters.parameter.clear()                 
            if view.name == 'xilinx_testbench':  
                view.modelName = static_setup_data["tb_top_entity"] 
                view.parameters.parameter.clear()                 
            if view.name == 'viewChecksum':                 
                view.parameters.parameter.clear()  
                                                                   
        pyxb.RequireValidWhenGenerating(False)
        pyxb.utils.domutils.BindingDOMSupport.DeclareNamespace(binding.Namespace, 'spirit')
        spirit_xml_string = component.toxml("utf-8", element_name='spirit:component').decode('utf-8')      
        
        # ----------------------------------
        # correct wrong sequences
        # add scema locations for validation
        # ----------------------------------
        namespaces = dict([
             node for _, node in ET.iterparse(
                 StringIO(spirit_xml_string), events=['start-ns']
             )
        ])        
        namespaces["xilinx"] = "http://www.xilinx.com"
        
        for name, value in namespaces.items():
            ET.register_namespace(name, value)
                   
        tree = ET.ElementTree(ET.fromstring(spirit_xml_string))
        root = tree.getroot()
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance" )
        root.set("xsi:schemaLocation", "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009 ./../submodules/setup2amd/schemas/SPIRIT/1685-2009/index.xsd http://www.xilinx.com ./../submodules/setup2amd/schemas/xilinx/xilinx.xsd" )
        
        wiresElement = root.findall("./spirit:model/spirit:ports/spirit:port/spirit:wire", namespaces)
        for wireElement in wiresElement:
            directionElement = wireElement.find("./spirit:direction", namespaces)
            wireElement.remove(directionElement)
            wireElement.insert(0, directionElement)
            
        fileSetsElement = root.find("./spirit:fileSets", namespaces)
        for fileSetElement in fileSetsElement:
            fileElements = fileSetElement.findall("./spirit:file", namespaces)
            for fileElement in fileElements:               
                logicalNameElement = fileElement.find("./spirit:logicalName", namespaces)
                if logicalNameElement is not None:
                    fileElement.remove(logicalNameElement)
                    position = len(list(fileElement)) - 1
                    logicalNameElement.insert(position, logicalNameElement)
 
        busInterfacesElement = root.find("./spirit:busInterfaces", namespaces)
        for busInterfaceElement in busInterfacesElement:
            busInterfaceNameElement = busInterfaceElement.find("./spirit:name", namespaces)
            busInterfaceElement.remove(busInterfaceNameElement)
            busInterfaceSlaveElement = busInterfaceElement.find("./spirit:slave", namespaces)
            busInterfaceElement.remove(busInterfaceSlaveElement)
            busInterfaceElement.insert(0, busInterfaceNameElement)
            busInterfaceElement.insert(3, busInterfaceSlaveElement)
            busInterfaceParametersElement = busInterfaceElement.find("./spirit:parameters", namespaces)
            if busInterfaceParametersElement is not None:
                for busInterfaceparameterElement in busInterfaceParametersElement:
                    busInterfaceparameterNameElement = busInterfaceparameterElement.find("./spirit:name", namespaces)
                    busInterfaceparameterElement.remove(busInterfaceparameterNameElement)
                    busInterfaceparameterElement.insert(0, busInterfaceparameterNameElement)
         
        parametersElement = root.find("./spirit:parameters", namespaces)            
        if parametersElement is not None:
            for parameterElement in parametersElement:
                parameterNameElement = parameterElement.find("./spirit:name", namespaces)
                parameterElement.remove(parameterNameElement)
                parameterElement.insert(0, parameterNameElement)
                if parameterNameElement.text  == "Component_Name":
                    parameterValueElement = parameterElement.find("./spirit:value", namespaces)
                    parameterValueElement.text = static_setup_data["top_entity"] + "_v1_0"
                
        viewsElement = root.find("./spirit:model/spirit:views", namespaces)            
        if viewsElement is not None:
            for viewElement in viewsElement:
                viewNameElement = viewElement.find("./spirit:name", namespaces)
                viewElement.remove(viewNameElement)
                viewElement.insert(0, viewNameElement)

                viewEnvIdentifierElement = viewElement.find("./spirit:envIdentifier", namespaces)
                viewElement.remove(viewEnvIdentifierElement)
                viewElement.insert(3, viewEnvIdentifierElement)
                
                viewLanguageElement = viewElement.find("./spirit:language", namespaces)
                if viewLanguageElement is not None:
                    viewElement.remove(viewLanguageElement)
                    viewElement.insert(4, viewLanguageElement)
                    
                viewModelNameElement = viewElement.find("./spirit:modelName", namespaces)
                if viewModelNameElement is not None:
                    viewElement.remove(viewModelNameElement)
                    if viewLanguageElement is not None:
                        viewElement.insert(5, viewModelNameElement)
                    else :
                        viewElement.insert(4, viewModelNameElement)
                        
                viewParametersElement = viewElement.find("./spirit:parameters", namespaces)
                if viewParametersElement is not None:
                    if len(list(viewParametersElement)) == 0:
                        viewElement.remove(viewParametersElement)
                    else:
                        viewElement.remove(viewParametersElement)
                        viewElement.insert(5, viewParametersElement)  
                                     
        viewParametersElement = root.find("./spirit:model/spirit:views/spirit:view/spirit:parameters", namespaces)            
        if viewParametersElement is not None:
            for viewParameterElement in viewParametersElement:
                viewParameterNameElement = viewParameterElement.find("./spirit:name", namespaces)
                viewParameterElement.remove(viewParameterNameElement)
                viewParameterElement.insert(0, viewParameterNameElement)                        

        vendor = tree.find("./spirit:vendor", namespaces) 
        library = tree.find("./spirit:library", namespaces) 
        name = tree.find("./spirit:name", namespaces)  
        version = tree.find("./spirit:version", namespaces)                                      
        busInterfaces = tree.find("./spirit:busInterfaces", namespaces)
        memoryMaps = tree.find("./spirit:memoryMaps", namespaces)  
        model = tree.find("./spirit:model", namespaces) 
        choices = tree.find("./spirit:choices", namespaces) 
        fileSets = tree.find("./spirit:fileSets", namespaces)    
        description = tree.find("./spirit:description", namespaces)    
        parameters = tree.find("./spirit:parameters", namespaces)       
        
        root.remove(vendor)
        root.remove(library)
        root.remove(name)
        root.remove(version)
        root.remove(busInterfaces)
        root.remove(memoryMaps)
        root.remove(model)
        root.remove(choices)
        root.remove(fileSets)
        root.remove(description)
        root.remove(parameters)
        
        root.append(vendor)
        root.append(library)
        root.append(name)
        root.append(version)
        root.append(busInterfaces)
        root.append(memoryMaps)
        root.append(model)
        root.append(choices)
        root.append(fileSets)
        root.append(description)
        root.append(parameters)        
                                       
        # --------------------------------
        # add and modify vendor extensions 
        # --------------------------------        
        
        root.append(vendorExtensions)
        
        # print(ET.tostring(root, encoding='utf8').decode('utf8'))
        
        displayNameElement = root.find("./spirit:vendorExtensions/xilinx:coreExtensions/xilinx:displayName", namespaces)
        displayNameElement.text = static_setup_data["top_entity"] + "_v1_0"
        coreExtensionsElement = root.find("./spirit:vendorExtensions/xilinx:coreExtensions", namespaces)
        coreExtensionsTagsElement = root.find("./spirit:vendorExtensions/xilinx:coreExtensions/xilinx:tags", namespaces)
        coreExtensionsElement.remove(coreExtensionsTagsElement)
        
        packagingInfo = root.find("./spirit:vendorExtensions/xilinx:packagingInfo", namespaces)        
        for elem in packagingInfo.iter():
            for child in list(elem):
                if child.tag == '{' + namespaces["xilinx"] + '}' + 'checksum':
                    elem.remove(child)
              
        spirit_amd_xml_string = ET.tostring(root, encoding='utf8').decode('utf8')
        
        xml_ugly = minidom.parse(StringIO(spirit_amd_xml_string))
        self.remove_blanks(xml_ugly)
        xml_ugly.normalize()
        pretty_spirit_xml_string = xml_ugly.toprettyxml(indent = '  ')
        
        # print(ET.tostring(root, encoding='utf8').decode('utf8'))
        
        print("writing {}".format(component_xml_file_path))
        component_xml_file = open(component_xml_file_path, 'w')
        component_xml_file.write(pretty_spirit_xml_string)
        component_xml_file.close()
        
    def remove_blanks(self, node):
        for x in node.childNodes:
            if x.nodeType == Node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == Node.ELEMENT_NODE:
                self.remove_blanks(x)

@click.command()
@click.option('--infile', default='../../../setup.py',  help='setup_py_file_path')
@click.option('--infile_component_axilite_template', default='templates/component_axilite_template.xml',  help='component_axilite_template_path')
@click.option('--outfile_component_xml', default='../../../package/component.xml',  help='component_xml_file_path')
def generate(infile, infile_component_axilite_template, outfile_component_xml):
    obj = SetupToSpiritComponent()
    obj. generate(setup_py_file_path=infile, 
                  component_axilite_template_path=infile_component_axilite_template,
                  component_xml_file_path=outfile_component_xml
                  )

if __name__ == '__main__':
    generate()
