# flywheel/hcp-diff
[Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) that runs the diffusion preprocessing steps of the [Human Connectome Project](http://www.humanconnectome.org) Minimal Preprocessing Pipeline (MPP) described in [Glasser et al. 2013](http://www.ncbi.nlm.nih.gov/pubmed/23668970).  This includes correction for EPI distortion (using [FSL topup](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup/TopupUsersGuide)), correction for motion and eddy-current distortion (using [FSL eddy](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy)), and registration to subject anatomy. For more info on the pipelines, see [HCP Pipelines](https://github.com/Washington-University/Pipelines).

## Important notes
* Diffusion time series must be provided in pairs with opposite phase-encoding.
* All MRI inputs must include BIDS-conformed DICOM metadata!
* Gradient nonlinearity correction (using coefficient file) is currently only available for data from Siemens scanners.

## Required inputs
1. Pair of diffusion scans (each including NiFTI+bvec+bval) with identical acquisitions but opposite phase-encoding (R>>L + L>>R, *or* P>>A + A>>P)
3. StructZip output from the HCP-Struct gear (containing <code>T1w/</code>, <code>T2w/</code>, and <code>MNINonLinear/</code> folders)
4. FreeSurfer license.txt file  (found in <code>$FREESURFER_HOME/license.txt</code>)

## Optional inputs
1. Additional diffusion pairs *from the same session* (DWIPositiveData2 + DWINegativeData2, etc...)
2. Gradient nonlinearity coefficients copied from scanner. See [FAQ 8. What is gradient nonlinearity correction?](https://github.com/Washington-University/Pipelines/wiki/FAQ#8-what-is-gradient-nonlinearity-correction)
    * If needed, this file can be obtained from the console at <code>C:\MedCom\MriSiteData\GradientCoil\coeff.grad</code> for Siemens scanners
    * Note: This effect is significant for HCP data collected on custom Siemens "ConnectomS" scanner, and for 7T scanners.  It is relatively minor for production 3T scanners (Siemens Trio, Prisma, etc.)

## Outputs
* <code>\<subject\>\_\<DWIName\>\_hcpdiff.zip</code>: Zipped output directory containing <code>\<subject\>/<DWIName\>/</code> and <code>\<subject\>/T1w/<DWIName\>/</code> folders
* <code>\<subject\>\_\<DWIName\>\_hcpdiff\_QC.*.png</code>: QC images for visual inspection of output quality (details to come...)
* Logs (details to come...)

## Important HCP Pipeline links
* [HCP Pipelines](https://github.com/Washington-University/Pipelines)
* [HCP Pipelines FAQ](https://github.com/Washington-University/Pipelines/wiki/FAQ)
* [HCP Pipelines v3.4.0 release notes](https://github.com/Washington-University/Pipelines/wiki/v3.4.0-Release-Notes,-Installation,-and-Usage)
