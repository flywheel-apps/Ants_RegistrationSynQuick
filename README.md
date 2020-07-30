# Ants_RegistrationSynQuick


This gear runs the [ANTS RegistrationSynQuick tool](https://nipype.readthedocs.io/en/1.1.7/interfaces/generated/interfaces.ants/registration.html#registrationsynquick).
RegistrationSynQuick is an ANTS registration tool that automatically handles many of the finicky 
registration options normally needed for ANTS registration.

We strongly recommend that you familiarize yourself with this script before using this gear by reading their [documentation](https://github.com/ANTsX/ANTs/blob/master/Scripts/antsRegistrationSyN.sh)

## Gear Operation

This gear will register one image to another, by default an MNI template.

This gear allows the user to specify if the input T1 is skull stripped or not.  If the input image is skull stripped,
it will be registered to a skull-stripped template.


### Inputs:


- `moving_image`:   The moving image to be registered
- `fixed_image`:    The fixed image that the moving image is registered to the [ICBM 2009a Nonlinear Asymmetric template](http://nist.mni.mcgill.ca/?p=904)


### Settings:

#### RegistrationSynQuick Settings:

These map directly to the arguments described in [regz](https://github.com/ANTsX/ANTs/blob/master/Scripts/antsRegistrationSyN.sh#L48)
- `args`: A string of any additional parameters to the command.
- `dimension`: image dimension (2 or 3).
- `histogram_bins`: Histogram bins for mutual information in SyN stage.
- `output_prefix`: A prefix that is prepended to all output files.
- `precision_type`: Double or Float
- `spline_distance`: Spline distance for deformable B-spline SyN transform
- `transform_type`: Transform type\nt: translation\nr: rigid\na: rigid + affine\ns: rigid + affine + deformable syn (default)\nsr: rigid + deformable syn\nb: rigid + affine + deformable b-spline syn\nbr: rigid + deformable b-spline syn
- `use_histogram_matching`: Use histogram matching.

#### Flywheel Settings:
- `skullstrip_standard_image`: Use this option if you are registering to the standard image, but your moving image has no skull.
- `save_transform`: Save transformation information (matrix, warps, inverse warp, etc).

### Output:

The output will be a zipped file containing the transformed image, and if "save_transform"
is selected, additional transformation information is also saved, such as the transformation matrix, transformation warps, etc.

