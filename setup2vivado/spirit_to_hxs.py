'''
Created on Feb 26, 2023

@author: dev
'''
import pyxb
from spirit_1685_2009 import binding
from hxs.hxs_enum import HxSEnum
from hxs.hxs_value import HxSValue
from hxs.hxs_bits import HxSBitBehavior
from hxs.hxs_register import HxSRegister
from hxs.hxs_block import HxSBlock
from hxs.hxs_interface import HxSInterface
from hxs.hxs_namespace import HxSNamespace 

class ToHxs:

    def read(self):
        xml_path = './samples_spirit/axi_uartlite/component.xml'
        xml = open(xml_path).read()  
        try:
            component = binding.CreateFromDocument(xml, location_base='./samples_spirit/axi_uartlite/component.xml')
        except pyxb.ValidationError as e:
            print(e.details())
        print('component.vendor ' + component.vendor)   
        print('component.library ' + component.library)            
        print('component.name ' + component.name)
        print('component.version ' + component.version)
        namespace = HxSNamespace()
        namespace.id = f'{component.vendor}.{component.library}'
        namespace.interfaces = []
        for memMapIdx, memMap in enumerate(component.memoryMaps.memoryMap):
            interface = HxSInterface()
            interface.id = f'MemoryMap{memMapIdx}'
            interface.blocks =[]
            for _addrBlockIdx, addrBlock in enumerate(memMap.addressBlock):
                block = HxSBlock()
                block.id = f'{addrBlock.name}'
                if addrBlock.description is not None:
                    block.description = f'{addrBlock.description}'
                block.base_address =  f'{addrBlock.baseAddress.value()}'
                block.size =  f'{addrBlock.range.value()}'      
                # print('  addrBlock.width.value() {}'.format(addrBlock.width.value()))
                # print('  addrBlock.usage {}'.format(addrBlock.usage))
                # TODO: use block width and usage
                if addrBlock.volatile is not None:
                    print('  addrBlock.volatile {}'.format(addrBlock.volatile))
               
                if addrBlock.access is None:
                    block_access = 'read-write'    
                else:    
                    block_access = '{}'.format(addrBlock.access) 
                block.registers = []
                for _regIdx, reg in enumerate(addrBlock.register):
                    register = HxSRegister()
                    register.id = f'{reg.name}'
                    if reg.description is not None:
                        register.description = f'{reg.description}'
                    register.addressOffset = f'{reg.addressOffset}'
                    register.size = f'{reg.size.value()}'
                    reg_volatile = f'{reg.volatile}'          
                    if reg.access is None:
                        reg_access = block_access
                    else:    
                        reg_access = '{}'.format(reg.access)
                    register.bits = [] 
                    for _fieldIdx, field in enumerate(reg.field):
                        enum = HxSEnum()
                        enum.id = '{}'.format(field.name)
                        if field.description is not None:
                            enum.description = '{}'.format(field.description)  
                        enum.position = '{}'.format(field.bitOffset) 
                        enum.width = '{}'.format(field.bitWidth.value()) 
                        enum.bits = []
                        if field.access is None:
                            field_access = reg_access
                        else:
                            field_access = '{}'.format(field.access) 
                            # Indicates the accessibility of the data in the address bank, address block, register or field.  
                            # Possible values are 'read-write', 'read-only',  'write-only', 'writeOnce' and 'read-writeOnce'. 
                            # If not specified the value is inherited from the containing object.
                            if reg_volatile =='true':
                                if field_access == 'read-write':
                                    enum.behaviour = HxSBitBehavior.REGISTER                 
                                elif field_access == 'read-only':
                                    enum.behaviour = HxSBitBehavior.READ_TRANSPARENT
                                elif field_access == 'write-only':
                                    enum.behaviour = HxSBitBehavior.WRITE_TRANSPARENT
                                elif field_access == 'writeOnce':
                                    enum.behaviour = HxSBitBehavior.WRITE_TRANSPARENT
                                elif field_access == 'read-writeOnce':
                                    enum.behaviour = HxSBitBehavior.REGISTER
                            else:
                                if field_access == 'read-write':
                                    enum.behaviour = HxSBitBehavior.TRANSPARENT                
                                elif field_access == 'read-only':
                                    enum.behaviour = HxSBitBehavior.READ_TRANSPARENT
                                elif field_access == 'write-only':
                                    enum.behaviour = HxSBitBehavior.WRITE_TRANSPARENT
                                elif field_access == 'writeOnce':
                                    enum.behaviour = HxSBitBehavior.WRITE_TRANSPARENT
                                elif field_access == 'read-writeOnce':
                                    enum.behaviour = HxSBitBehavior.TRANSPARENT                                
                                
                            # TODO: field.access specialities                           
                        if field.enumeratedValues is not None:          
                            for _enmIdx, enumVal in enumerate(field.enumeratedValues.enumeratedValue):
                                value = HxSValue()
                                value.id = '{}'.format(enumVal.name)
                                value.value = '{}'.format(enumVal.value_.value())   
                                enum.values.append(value)
                        register.bits.append(enum)            
                    block.registers.append(register)
                interface.blocks.append(block)
            namespace.interfaces.append(interface)
        
        for line in namespace.hxs():
            print(f'{line}')
        
                        
if __name__ == '__main__':
    f = ToHxs()
    f. read()