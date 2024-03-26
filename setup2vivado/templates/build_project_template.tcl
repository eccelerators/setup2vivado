set project_origin "../"
set project_work  "work"
set project_name "{{ name }}"
set project_part "xczu3eg-sfvc784-1-i"
set project_src  "src"
set project_tb  "tb"
set project_ip "ip"
set project_package "package"

proc printMessage {outMsg} {
    puts " --------------------------------------------------------------------------------"
    puts " -- $outMsg"
    puts " --------------------------------------------------------------------------------"
}

printMessage "Project: ${project_name}   Part: ${project_part}   Source Folder: ${project_src}"

# Create project
printMessage "Create the Vivado project"
create_project ${project_name} ${project_work} -part ${project_part} -force

# Set the directory path for the new project
set proj_dir [get_property directory [current_project]]

# Set project properties
set obj [current_project]
set_property -name "default_lib" -value "xil_defaultlib" -objects $obj
set_property -name "ip_cache_permissions" -value "read write" -objects $obj
set_property -name "ip_output_repo" -value "${project_work}/${project_name}.cache/ip" -objects $obj
set_property -name "part" -value ${project_part} -objects $obj
set_property -name "sim.ip.auto_export_scripts" -value "1" -objects $obj
set_property -name "simulator_language" -value "Mixed" -objects $obj
set_property -name "target_language" -value "VHDL" -objects $obj
set_property -name "xpm_libraries" -value "XPM_CDC XPM_FIFO XPM_MEMORY" -objects $obj
set_property -name "xsim.array_display_limit" -value "64" -objects $obj

# Need to enable VHDL 2008
set_param project.enableVHDL2008 1

#------------------------------------------------------------------------
printMessage "Include VHDL files into project"

if {[string equal [get_filesets -quiet sources_1] ""]} {
  create_fileset -srcset sources_1
}

set obj [get_filesets sources_1]
set files_vhd [list \
 {% for src_data_file in src_data_file_list %}"[file normalize "{{ src_data_file["file"] }}"]" \
 {% endfor %}]
add_files -norecurse -fileset $obj $files_vhd

{% for src_data_file in src_data_file_list %}
set file "{{ src_data_file['file'] }}"
set file [file normalize $file]
set file_obj [get_files -of_objects [get_filesets sources_1] [list "*$file"]]
set_property -name "file_type" -value "{{ src_data_file['file_type'] }}" -objects $file_obj
{% if src_data_file.get('library') is not none %}set_property -name "library" -value "{{ src_data_file['library'] }}" -objects $file_obj
{% endif %}{% endfor %}

set obj [get_filesets sources_1]
set_property -name "top" -value "{{ top_entity }}" -objects $obj
set_property -name "top_auto_set" -value "0" -objects $obj
set_property -name "top_file" -value "{{ top_entity_file }}" -objects $obj

#------------------------------------------------------------------------
printMessage "Synthesizing..."

launch_runs synth_1 -jobs 4

close_project -verbose

#------------------------------------------------------------------------
printMessage "Project: ${project_name}   Part: ${project_part}   Source Folder: ${project_src}"
