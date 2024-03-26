import pyxb
from spirit_1685_2009 import binding


class SpiritComponentDump:

    def dump(self, xml_string):
        try:
            component = binding.CreateFromDocument(xml_string)
        except pyxb.ValidationError as e:
            print(e.details())
        print('component.vendor ' + component.vendor)   
        print('component.library ' + component.library)            
        print('component.name ' + component.name)
        print('component.version ' + component.version)
           
        for _memMapIdx, memMap in enumerate(component.memoryMaps.memoryMap):
            for _addrBlockIdx, addrBlock in enumerate(memMap.addressBlock):
                print('  addrBlock.name {}'.format(addrBlock.name))
                if addrBlock.description is not None:
                    print('  addrBlock.description {}'.format(addrBlock.description))
                print('  addrBlock.baseAddress.value() {}'.format(addrBlock.baseAddress.value()))
                print('  addrBlock.range.value() {}'.format(addrBlock.range.value()))
                print('  addrBlock.width.value() {}'.format(addrBlock.width.value()))
                print('  addrBlock.usage {}'.format(addrBlock.usage))
                if addrBlock.volatile is not None:
                    print('  addrBlock.volatile {}'.format(addrBlock.volatile))
                print('  addrBlock.access {}'.format(addrBlock.access))
                for _regIdx, reg in enumerate(addrBlock.register):
                    print('    reg.name {}'.format(reg.name))
                    if reg.description is not None:
                        print('    reg.description {}'.format(reg.description))
                    print('    reg.addressOffset.value() {}'.format(reg.addressOffset))
                    print('    reg.size.value() {}'.format(reg.size.value()))
                    print('    reg.volatile {}'.format(reg.volatile))
                    print('    reg.access {}'.format(reg.access))
                    for _fieldIdx, field in enumerate(reg.field):
                        print('      field.name {}'.format(field.name))
                        if field.description is not None:
                            print('      field.description {}'.format(field.description))                        
                        print('      field.bitOffset {}'.format(field.bitOffset))                      
                        print('      field.bitWidth.value() {}'.format(field.bitWidth.value()))
                        print('      field.access {}'.format(field.access))       
                        if field.enumeratedValues is not None:                    
                            for _enmIdx, enumVal in enumerate(field.enumeratedValues.enumeratedValue):
                                print('      enumVal.name {}'.format(enumVal.name))
                                print('      rstVal.value_.value() {}'.format(enumVal.value_.value()))
                                                                
        for _portIdx, port in enumerate(component.model.ports.port):
            print('  port.name {}'.format(port.name))
            wire = port.wire
            print('    wire.direction {}'.format(wire.direction))
            vector = wire.vector
            if vector is not None:
                print('    vectorLeft {}'.format(vector.left.value()))
                print('    vectorRight {}'.format(vector.right.value())) 
            wireTypeDefs = wire.wireTypeDefs
            for _wireTypeDefIdx, wireTypeDef in enumerate(wireTypeDefs.wireTypeDef):
                typeName = wireTypeDef.typeName
                print('      typeName {}'.format(typeName.value()))            
                for _viewNameRef, viewNameRef in enumerate(wireTypeDef.viewNameRef):
                    print('      viewNameRef {}'.format(viewNameRef))

        for _fileSetIdx, fileSet in enumerate(component.fileSets.fileSet):
            print('  fileSet.name {}'.format(fileSet.name))
            for _fileIdx, file in enumerate(fileSet.file):
                print('  file.name {}'.format(file.name.value()))
                         
if __name__ == '__main__':
    xml_path = 'test/component.xml'
    xml_string = open(xml_path).read()  
    f = SpiritComponentDump()
    f. dump(xml_string)