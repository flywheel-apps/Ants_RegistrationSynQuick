#!/usr/bin/env python3.7

from nipype import Node, Function, Workflow
import nipype.interfaces.ants as ants
from nipype.interfaces.io import DataSink
from nipype.interfaces.ants import RegistrationSynQuick
from pathlib import Path
from ast import literal_eval
import shutil
import logging
import os
import flywheel_gear_toolkit as ft


log = logging.getLogger()

def skullstrip_standard_node():
    skullstrip_standard = Node(ants.MultiplyImages(
        dimension=3,
        first_input='/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a.nii',
        second_input='/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a_mask.nii',
        output_product_image='/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a_brain.nii'),
        name='skullstrip_standard_node')

    return (skullstrip_standard)


def create_registration_node(config, moving_image):
    log.info('Creating Registration node...')

    reg = Node(RegistrationSynQuick(), name='registration_node')

    for key, val in reg.inputs.items():

        if key in config:
            config_val = config[key]
            reg.set_input(key, config_val)

    warped_output = 'warped_output.nii'
    reg.inputs.moving_image = moving_image

    log.debug(reg.inputs)
    log.info('...Complete!')

    return (reg)


def make_workflow(config, strip_standard, moving_image, fixed_image,
                  fixed_is_standard, output_dir):
    log.info('Creating Workflow...')
    # Declare and create output directories
    workflow_directory = '/flywheel/v0/nipype/workflow'
    Path(workflow_directory).mkdir(parents=True)

    wf = Workflow(name='moving2fixed', base_dir=workflow_directory)

    # Create the registration node
    registration_node = create_registration_node(config, moving_image)

    # If the fixed image is standard and we are to skullstrip it, do that
    log.debug('\tChecking if fixed is standard')
    if strip_standard and fixed_is_standard:
        log.debug('\t fixed is standard, and skull strip true.  Adding strip node')
        skullstrip_node = skullstrip_standard_node()
        log.debug('\tconnecting to wf')
        wf.connect(skullstrip_node, "output_product_image", registration_node, "fixed_image")
    else:
        log.debug('adding fixed image to registration node')
        registration_node.inputs.fixed_image = fixed_image

    # Create data sink for output
    log.debug('\tCreating sink')
    sink = Node(DataSink(), name='sinker')

    # Set the sink output to the flywheel output
    log.debug(f'\tSetting sink output to {output_dir}')
    sink.inputs.base_directory = output_dir
    wf.connect(registration_node, 'warped_image', sink, 'Registered_image')
    if config['save_transform']:
        log.debug('\tsaving transformation parameters')
        wf.connect(registration_node, 'forward_warp_field', sink, 'forward_warp_field')
        wf.connect(registration_node, 'inverse_warp_field', sink, 'inverse_warp_field')
        wf.connect(registration_node, 'out_matrix', sink, 'out_matrix')

    log.info('...Complete!')

    return (wf)


def collect_settings(context):
    log.info('Collecting settings...')
    config = context.config

    # Log settings in debug log
    for key, val in config.items():
        log.debug('\t{}: {}'.format(key, val))

    # Find if we need to skullstrip our standard images
    strip_standard = config.get('skullstrip_standard_image')

    # Get our moving image
    moving_image = context.get_input_path('moving_image')

    # Determine if we're using a user provided fixed image or the standard MNI
    if context.get_input_path('fixed_image'):
        fixed_image = context.get_input_path('fixed_image')
        standard = False
    else:
        fixed_image = '/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a.nii'
        standard = True

    log.info('...Complete!')
    # Return all this junk, all this junk up in your trunk
    return (config, strip_standard, moving_image, fixed_image, standard)


def cleanup(output_dir):
    log.info('cleaning up...')
    log.debug('\tmaking zip archive of output dir')
    shutil.make_archive('/flywheel/v0/zipped_out_dir', 'zip', output_dir)
    log.debug('\tremoving output dir')
    shutil.rmtree(output_dir)
    log.debug('\trecreating output dir')
    os.mkdir(output_dir)
    log.debug('\t moving zipped archive to output dir')
    shutil.move('/flywheel/v0/zipped_out_dir.zip', '{}/zipped_out_dir.zip'.format(output_dir))
    log.info('...Complete!')
