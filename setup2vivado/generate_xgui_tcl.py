from jinja2 import Environment, FileSystemLoader
from json import loads
from pathlib import Path
from setup_data_to_json import SetupToJson

import click

class SetupToXguiTcl:

    def generate(self, setup_py_file_path='test/setup.py', xgui_template_tcl_file_path='test/xgui_template.tcl', xgui_dir_path='test'):
        
        # --------------------------
        # extract data from setup.py
        # --------------------------
        extractor = SetupToJson()
        file_path = open(setup_py_file_path, 'r')     
        print("reading {}".format(setup_py_file_path))
        json_string = extractor.extract(setup_py_file_path)
        static_setup_data = loads(json_string)
        
        # -------------------------------------
        # prepare xgui tcl file
        # -------------------------------------        
        print("reading {}".format(xgui_template_tcl_file_path))   
        xgui_template_file = open(xgui_template_tcl_file_path, 'r')
        xgui_template_string = xgui_template_file.read()
        xgui_template_file.close()
        xgui_tcl_file_path = xgui_dir_path + '/' + static_setup_data["top_entity"] + "_v1_0" + ".tcl"
        print("writing {}".format(xgui_tcl_file_path))
        xgui_tcl_file = open(xgui_tcl_file_path, 'w')
        xgui_tcl_file.write(xgui_template_string)
        xgui_tcl_file.close()


@click.command()
@click.option('--infile', default='../../../setup.py',  help='setup_py_file_path')
@click.option('--templatefile_xgui', default='templates/xgui_template.tcl',  help='xgui_template_tcl_file_path')
@click.option('--outdir_xgui', default='../../../package/xgui',  help='xgui_dir_path')
def generate(infile, templatefile_xgui, outdir_xgui):
    obj = SetupToXguiTcl()
    obj. generate(setup_py_file_path=infile, 
                  xgui_template_tcl_file_path=templatefile_xgui,
                  xgui_dir_path=outdir_xgui
                  )
              

if __name__ == '__main__':
    generate()

