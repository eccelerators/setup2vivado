from jinja2 import Environment, FileSystemLoader, Template
from json import loads
from pathlib import Path
from setup_data_to_json import SetupToJson

import click

class GenerateTcl:
    
    def generate(self, 
                 setup_py_file_path='test/setup.py', 
                 create_template_tcl_file_path='test/create_project_template.tcl', 
                 build_template_tcl_file_path='test/build_project_template.tcl', 
                 create_tcl_file_path='test/create_project.tcl', 
                 build_tcl_file_path='test/build_project.tcl'):
        extractor = SetupToJson()
        file_path = open(setup_py_file_path, 'r')     
        print("reading {}".format(setup_py_file_path))
        json_string = extractor.extract(setup_py_file_path)
        static_setup_data = loads(json_string)
        
        src_data_file_list = []
        for src_data_file_per_dest in static_setup_data["src_data_files"]:                       
            for src_data_file in src_data_file_per_dest[1]:
                src_data_file_list.append(src_data_file)   
         
        tb_data_file_list = []
        for tb_data_file_per_dest in static_setup_data["tb_data_files"]:                       
            for tb_data_file in tb_data_file_per_dest[1]:
                tb_data_file_list.append(tb_data_file) 
                        
        context = {
                "name" : static_setup_data["project_name"],
                "top_entity" : static_setup_data["top_entity"],
                "top_entity_file" : static_setup_data["top_entity_file"], 
                "src_data_file_list" : src_data_file_list,
                "tb_top_entity" : static_setup_data["tb_top_entity"],
                "tb_top_entity_file" : static_setup_data["tb_top_entity_file"],    
                "tb_data_file_list" : tb_data_file_list,
            }     

        create_template_tcl_file = open(create_template_tcl_file_path, 'r')     
        print("reading {}".format(create_template_tcl_file_path))                           
        print("writing {}".format(create_tcl_file_path)) 
        template = Template(create_template_tcl_file.read())
        r = template.render(context)
        f = open(create_tcl_file_path, 'w')
        f.write(r)
        f.close()

        build_template_tcl_file = open(build_template_tcl_file_path, 'r')     
        print("reading {}".format(build_template_tcl_file))          
        print("writing {}".format(build_tcl_file_path))  
        template = Template(build_template_tcl_file.read())
        r = template.render(context)
        f = open(build_tcl_file_path, 'w')
        f.write(r)
        f.close()
        
        
@click.command()
@click.option('--infile', default='../../../setup.py',  help='setup_py_file_path')
@click.option('--templatefile_create', default='templates/create_project_template.tcl',  help='create_template_tcl_file_path')
@click.option('--templatefile_build', default='templates/build_project_template.tcl',  help='build_template_tcl_file_path')
@click.option('--outfile_create', default='../../../scripts/create_project.tcl',  help='create_tcl_file_path')
@click.option('--outfile_build', default='../../../scripts/build_project.tcl',  help='build_tcl_file_path')
def generate(infile, templatefile_create, templatefile_build, outfile_create, outfile_build):
    obj = GenerateTcl()
    obj. generate(setup_py_file_path=infile, 
                  create_template_tcl_file_path=templatefile_create, build_template_tcl_file_path=templatefile_build,
                  create_tcl_file_path=outfile_create, build_tcl_file_path=outfile_build
                  )

if __name__ == '__main__':
    generate()



