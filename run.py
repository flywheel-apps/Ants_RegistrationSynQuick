from nipype import Node, Function, Workflow
import nipype.interfaces.ants as ants
from nipype.interfaces.io import DataSink
from pathlib import Path
from ast import literal_eval
import shutil
import logging
import os
import flywheel



 # Instantiate a logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('root')

def skullstrip_standard_node():
    skullstrip_standard = Node(ants.MultiplyImages(
        dimension=3,
        first_input='/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a.nii',
        second_input='/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a_mask.nii',
        output_product_image='/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a_brain.nii'),
        name='skullstrip_standard_node')

    return (skullstrip_standard)


def register_t1_2_standard_node(config):
    reg = Node(ants.Registration(), name='registration_node')
    
    for key, val in reg.inputs.items():
        
        if key in config:
            config_val = config[key]
            
            if isinstance(config_val,str):
                config_val = literal_eval(config_val)
            
            print('{}: {}'.format(key, config_val))
            reg.set_input(key, config_val)
    
    log.debug(reg.inputs)
    
    return (reg)


def make_workflow(input_t1, config, has_skull=True):
    
    workflow_directory = '/flywheel/v0/nipype/workflow'
    Path(workflow_directory).mkdir(parents=True)
    warped_output = 'warped_output.nii'
    
    standard = '/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a.nii'

    wf = Workflow(name='register2standard', base_dir=workflow_directory)

    registration_node = register_t1_2_standard_node(config)


    registration_node.inputs.moving_image = input_t1
    registration_node.inputs.fixed_image = standard
    registration_node.inputs.output_warped_image = warped_output
    
    

    if not has_skull:
        skullstrip_node = skullstrip_standard_node()

        wf.connect(skullstrip_node, "output_product_image", registration_node, "fixed_image")
    else:
        
        registration_node.inputs.fixed_image = standard


    sink = Node(DataSink(), name='sinker')

    # Name of the output folder
    sink.inputs.base_directory = '/flywheel/v0/output/sink'
    wf.connect(registration_node, 'warped_image', sink, 'T1_Out')
    
    return (wf)

        
def main():
    
    
    with flywheel.gear_context.GearContext() as context:
        
        
        config = context.config
        
        for key,val in config.items():
            log.debug('{}: {}'.format(key,val))
        
        has_skull = config['has-skull']
        input_t1 = context.get_input_path('t1w-input')
        
        
        wf = make_workflow(input_t1, config, has_skull=has_skull)
    
        wf.base_dir = '/flywheel/v0/output'
    
        # Connect DataSink with the relevant nodes
        
        wf.run()
    
        shutil.make_archive('/flywheel/v0/zipped_out_dir', 'zip', '/flywheel/v0/output')
        shutil.rmtree('/flywheel/v0/output')
        os.mkdir('/flywheel/v0/output')
        shutil.move('/flywheel/v0/zipped_out_dir.zip', '/flywheel/v0/output/zipped_out_dir.zip')


if __name__ == "__main__":
    main()
