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
import utils as ut



def main():
    
    with flywheel_gear_toolkit.GearToolkitContext() as gtk_context:
        # Setup basic logging
        gtk_context.init_logging()
        # Log the configuration for this job
        gtk_context.log_config()

        gtk_context.log.info('Collecting Gear config settings')
        config, strip_standard, moving_image, fixed_image, fixed_is_standard =\
            ut.collect_settings(gtk_context)
        
        gtk_context.log.info('Generating Workflow')
        wf = ut.make_workflow(config,
                           strip_standard,
                           moving_image,
                           fixed_image,
                           fixed_is_standard,
                           gtk_context.output_dir)
        
        # Run the WF
        gtk_context.log.info('Executing')
        wf.run()
        
        # Cleanup the files
        gtk_context.log.info('Cleaning Up')
        ut.cleanup(gtk_context.output_dir)
        


if __name__ == "__main__":
    main()
