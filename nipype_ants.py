from nipype import Node, Function, Workflow
import nipype.interfaces.ants as ants
from nipype.interfaces.io import DataSink



def skullstrip_standard_node():
    
    skullstrip_standard = Node(ants.MultiplyImages(
        dimension=3,
        first_input='/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a.nii',
        second_input='/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a_mask.nii',
        output_product_image='/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a_brain.nii'),
        name='skullstrip_standard_node')
    
    return(skullstrip_standard)
    
    
def register_t1_2_standard_node(metric, metric_weight, transforms,
                                smoothing_sigmas, shrink_factors, number_of_iterations,
                                transform_parameters):
    
    reg = Node(ants.Registration(metric=metric,
                      metric_weight=metric_weight,
                      transforms=transforms,
                      smoothing_sigmas=smoothing_sigmas,
                      shrink_factors=shrink_factors,
                      number_of_iterations=number_of_iterations,
                      transform_parameters = transform_parameters,
                      radius_or_number_of_bins = [32]*3,
                      output_transform_prefix = "output_",
                      dimension = 3,
                      write_composite_transform = True,
                      collapse_output_transforms = False,
                      initialize_transforms_per_stage = False,
                      sampling_strategy = ['Random', 'Random', None],
                      sampling_percentage = [0.05, 0.05, None],
                      convergence_threshold = [1.e-8,1.e-9,1.e-10],
                      convergence_window_size = [20]*3,
                      sigma_units = ['vox']*3,
                      output_warped_image = 'output_warped_image.nii.gz'),
               name='registration_node')

    
    return(reg)


def make_workflow(input_t1, metric, metric_weight, transforms,
                  smoothing_sigmas, shrink_factors,
                  number_of_iterations, transform_parameters, has_skull=True):
    
    standard = '/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a.nii'
    
    wf = Workflow(name='register2standard', base_dir='/flywheel/v0/work')
    
    registration_node = register_t1_2_standard_node(metric, metric_weight, transforms,
              smoothing_sigmas, shrink_factors,
              number_of_iterations, transform_parameters)
    
    registration_node.inputs.moving_image = input_t1
    registration_node.inputs.fixed_image = standard
    
    if not has_skull:
        skullstrip_node = skullstrip_standard_node()
        
        wf.connect(skullstrip_node, "output_product_image", registration_node, "fixed_image")
    else:
        registration_node.inputs.fixed_image = standard
        
    return(wf)


def test_pype():
    transforms = ['Rigid', 'Affine', 'SyN']
    metric = ['Mattes']*3
    metric_weight = [.7]*3
    smoothing_sigmas = [[1], [1], [0]]
    shrink_factors = [[1], [1],[1]]
    input_t1 = '/tmp/DICOM_T1w_BIC7T_V0_20200114085537_7_ns.nii.gz'
    number_of_iterations = [[100],[50],[10]]
    transform_parameters = [(0.1,), (0.1,), (0.1, 3.0, 0.0)]
    standard = '/flywheel/v0/templates/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a.nii'
    wf = make_workflow(input_t1, metric, metric_weight, transforms,
                       smoothing_sigmas, shrink_factors, number_of_iterations,
                       transform_parameters, has_skull=False)

    transforms = ['Rigid', 'Affine', 'SyN']
    metric = ['Mattes'] * 3
    metric_weight = [.7] * 3
    smoothing_sigmas = [[1], [1], [0]]
    shrink_factors = [[1], [1], [1]]
    input_t1 = '/Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears/nipype/DockerIO/DICOM_T1w_BIC7T_V0_20200114085537_7_ns.nii.gz'
    number_of_iterations = [[100], [50], [10]]
    transform_parameters = [(0.1,), (0.1,), (0.1, 3.0, 0.0)]
    standard = input_t1

    ari=Node(ants.Registration(metric=metric,
                      metric_weight=metric_weight,
                      transforms=transforms,
                      smoothing_sigmas=smoothing_sigmas,
                      shrink_factors=shrink_factors,
                      number_of_iterations=number_of_iterations,
                      fixed_image = standard,
                      moving_image = input_t1,
                      transform_parameters = transform_parameters,
                      radius_or_number_of_bins = [32]*3,
                      output_transform_prefix = "output_",
                      dimension = 3,
                      write_composite_transform = True,
                      collapse_output_transforms = False,
                      initialize_transforms_per_stage = False,
                      sampling_strategy = ['Random', 'Random', None],
                      sampling_percentage = [0.05, 0.05, None],
                      convergence_threshold = [1.e-8,1.e-9,1.e-10],
                      convergence_window_size = [20]*3,
                      sigma_units=['vox'] * 3),
                    name='reg_node')

    ari.inputs.output_warped_image = 'my_out.nii'
    sink = Node(DataSink(), name='sinker')

    # Name of the output folder
    sink.inputs.base_directory = '/tmp/sink'
    
    # Create a preprocessing workflow
    wf = Workflow(name="preprocWF")
    wf.base_dir = '/tmp/wf_dir'
    
    # Connect DataSink with the relevant nodes
    wf.connect(ari, 'warped_image', sink, 'T1_Out')
    wf.run()

    return(wf)

    # ari=ants.Registration(metric=metric,
    #                   metric_weight=metric_weight,
    #                   transforms=transforms,
    #                   smoothing_sigmas=smoothing_sigmas,
    #                   shrink_factors=shrink_factors,
    #                   number_of_iterations=number_of_iterations,
    #                   fixed_image = standard,
    #                   moving_image = input_t1,
    #                   transform_parameters = transform_parameters,
    #                   output_warped_image='/warpeed_out.nii',
    #                   verbose=True,
    #                   radius_or_number_of_bins = [32]*3)
    

