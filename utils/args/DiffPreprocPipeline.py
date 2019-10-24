from collections import OrderedDict
import os, os.path as op
from tr import tr
import shutil

from .common import build_command_list, exec_command
from ..diff_utils import make_sym_link
import logging

log = logging.getLogger(__name__)

# set -x
# ${RUN_DIFF} ${FSLDIR}/bin/fsl_sub ${QUEUE} ${FSLSUBOPTIONS} \
#    ${HCPPIPEDIR}/DiffusionPreprocessing/DiffPreprocPipeline.sh \
#     --path="${StudyFolder}" \
#     --subject="${Subject}" \
#     --dwiname="${DWIName}" \
#     --posData="${DWIPosList}" \
#     --negData="${DWINegList}" \
#     --PEdir="${PEdir}" \
#     --echospacing="${DwellTime}" \
#     --gdcoeffs="${GradientDistortionCoeffs}" \
#     --dof="${DOF_EPI2T1}" \
#     --b0maxbval="${b0maxbval}" \
#     --combine-data-flag="${CombineDataFlag}" \
#     --extra-eddy-arg="${ExtraEddyArgs}" ${EddyNonGpuArg} \
#     --printcom=$PRINTCOM

# pipeline_status_code=$?

# set +x
def build(context):
    environ = context.gear_dict['environ']
    config = context.config
    inputs = context._invocation['inputs']

    # Install FreeSurfer license file
    shutil.copy(context.get_input_path('FreeSurferLicense'),
                op.join(environ['FREESURFER_HOME'],'license.txt'))

    # Default Config Settings
    # DwellTime for DWI volumes
    EffectiveEchoSpacing = "NONE" 

    # no gradient correction unless we are provided with a .grad file
    GradientDistortionCoeffs = "NONE"

    if 'GradientCoeff' in inputs.keys():
        GradientDistortionCoeffs = context.get_input_path('GradientCoeff')

    # Set PEdir variable based on phase-encoding directions
    PEdir = ""
    pedir_pos = None
    pedir_neg = None
    if  ('DWIPositiveData' in inputs.keys()) and \
        ('DWINegativeData' in inputs.keys()):
        info_pos = inputs["DWIPositiveData"].object.info
        info_neg = inputs["DWINegativeData"].object.info
        if  ('PhaseEncodingDirection' in info_pos.keys()) and \
            ('PhaseEncodingDirection' in info_neg.keys()):
            pedir_pos = tr("ijk", "xyz", info_pos.PhaseEncodingDirection)
            pedir_neg = tr("ijk", "xyz", info_neg.PhaseEncodingDirection)
            if  ((pedir_pos, pedir_neg) == ("x-", "x")) or \
                ((pedir_pos, pedir_neg) == ("x", "x-")):
                PEdir = 1
            elif ((pedir_pos, pedir_neg) == ("y-", "y")) or \
                ((pedir_pos, pedir_neg) == ("y", "y-")):
                PEdir = 2
    ###Create the posData and negData lists####
    # posData and negData are '@'-delimited lists of nifti files on the command
    # line. We will build them, validate them, and link
    posData = []
    negData = []

    # Even With the DWIPos/Neg data checking out, above,
    # I am going to loop through everything to be more compact
    # making a lists of the pos/neg data/bvec/bval to validate later
    valid_data_pos = []
    valid_data_neg = []

    valid_PE_pos = []
    valid_PE_neg = []

    valid_bvecs_pos = []
    valid_bvecs_neg = []

    valid_bvals_pos = []
    valid_bvals_neg = []

    base_dir = op.join(context.work_dir,'tmp_input')
    for i in range(1,11):
        # i=1 is a special case here 
        # the list of Diffusion files follows the format of 
        # DWIPositiveData, DWIPositiveData2, ...3, ....
        if i==1:
            j=''
        else:
            j=i
        # We only add to posData and negData if both are present
        # If only one is present, warn them in validate()
        if  ('DWIPositiveData{}'.format(j) in inputs.keys()) and \
            ('DWINegativeData{}'.format(j) in inputs.keys()):
            # Save the filepaths for later:
            data_pos = context.get_input_path('DWIPositiveData{}'.format(j))
            data_neg = context.get_input_path('DWINegativeData{}'.format(j))

            # We know what we want the end result to be. We append to the list
            # and validate that it is correct in validate()
            posData.append(op.join(base_dir,'Pos{}'.format(i),'data.nii.gz'))
            negData.append(op.join(base_dir,'Neg{}'.format(i),'data.nii.gz'))
            # Making the directories for these as we go
            os.makedirs(op.join(base_dir,'Pos{}'.format(i)), exist_ok=True)
            os.makedirs(op.join(base_dir,'Neg{}'.format(i)), exist_ok=True)

            # Grab the Phase Encoding
            info_pos = inputs['DWIPositiveData{}'.format(j)].object.info
            info_neg = inputs['DWINegativeData{}'.format(j)].object.info
            if  ('PhaseEncodingDirection' in info_pos.keys()) and \
                ('PhaseEncodingDirection' in info_neg.keys()):
                PE_pos = tr("ijk", "xyz", info_pos['PhaseEncodingDirection'])
                PE_neg = tr("ijk", "xyz", info_neg['PhaseEncodingDirection'])
            else:
                PE_pos = None
                PE_neg = None

            # Grab each of the pos/neg bvec/bval files or make them None
            if 'DWIPositiveBvec{}'.format(j) in inputs.keys():
                bvecs_pos = context.get_input_path('DWIPositiveBvec')
            else:
                bvecs_pos = None

            if 'DWINegativeBvec{}'.format(j) in inputs.keys():
                bvecs_neg = context.get_input_path('DWINegativeBvec')
            else:
                bvecs_neg = None

            if 'DWIPositiveBval{}'.format(j) in inputs.keys():
                bvals_pos = context.get_input_path('DWIPositiveBval')
            else:
                bvals_pos = None

            if 'DWINegativeBval{}'.format(j) in inputs.keys():
                bvals_neg = context.get_input_path('DWINegativeBval')
            else:
                bvals_neg = None
            # Comparing Phase Encoding Direction of the first to the Phase
            # Encoding of all.
            # The redundancy (first cycle is the first one) helps reduce the 
            # complexity of the code.
            if (pedir_pos,pedir_neg) == (PE_pos,PE_neg):
                # making a lists of the pos/neg data/bvec/bval to validate
                valid_data_pos.append(data_pos)
                valid_data_neg.append(data_neg)

                valid_PE_pos.append(PE_pos)
                valid_PE_neg.append(PE_neg)                

                valid_bvecs_pos.append(bvecs_pos)
                valid_bvecs_neg.append(bvecs_neg)

                valid_bvals_pos.append(bvals_pos)
                valid_bvals_neg.append(bvals_neg)
            # if the phases are reversed, flip the order of our data/vecs/vals
            elif (pedir_pos,pedir_neg) == (PE_neg,PE_pos):
                # making a lists of the pos/neg data/bvec/bval to validate
                valid_data_pos.append(data_neg)
                valid_data_neg.append(data_pos)
                
                valid_PE_pos.append(PE_neg)
                valid_PE_neg.append(PE_pos)

                valid_bvecs_pos.append(bvecs_neg)
                valid_bvecs_neg.append(bvecs_pos)

                valid_bvals_pos.append(bvals_neg)
                valid_bvals_neg.append(bvals_pos)
            # If something is way different, fill them with 'None'
            else:
                valid_data_pos.append(None)
                valid_data_neg.append(None)
                
                valid_PE_pos.append(None)
                valid_PE_neg.append(None)

                valid_bvecs_pos.append(None)
                valid_bvecs_neg.append(None)

                valid_bvals_pos.append(None)
                valid_bvals_neg.append(None)     
            make_sym_link(
                valid_data_pos[i-1],
                op.join(base_dir,'Pos{}'.format(i),'data.nii.gz')
            )
            make_sym_link(
                valid_data_neg[i-1],
                op.join(base_dir,'Neg{}'.format(i),'data.nii.gz')
            )
            make_sym_link(
                valid_bvecs_pos[i-1],
                op.join(base_dir,'Pos{}'.format(i),'data.bvec')
            )
            make_sym_link(
                valid_bvecs_neg[i-1],
                op.join(base_dir,'Neg{}'.format(i),'data.bvec')
            )
            make_sym_link(
                valid_bvals_pos[i-1],
                op.join(base_dir,'Pos{}'.format(i),'data.bval')
            )
            make_sym_link(
                valid_bvals_neg[i-1],
                op.join(base_dir,'Neg{}'.format(i),'data.bval')
            )
            # TODO: I want to try to create symbolic links for these files
            #       instead of copying them: os.symlink(src, dst)
            #TODO: But the following section in validate()
            # elif [[ "${petmp1}" == "${petmp2}" ]]; then
            #     echo -e "$CONTAINER [$(timestamp)] ERROR: DWIPositiveData${i} and DWINegativeData${i} have the same PhaseEncodingDirection (${petmp1})!"
            #     exit 1
            # else
            #     echo -e "$CONTAINER [$(timestamp)] ERROR: DWI input pair #${i} phase-encoding directions (${petmp1},${petmp2}) do not match primary pair (${pedir_pos},${pedir_neg}). Exiting!"
            #     exit 1
        
    # Read necessary acquisition params from fMRI
    EffectiveEchoSpacing = ""
    if 'DWIPositiveData' in inputs.keys():
        info = inputs['DWIPositiveData']['object']['info']
        if 'EffectiveEchoSpacing' in info.keys():
            EffectiveEchoSpacing = format(info['EffectiveEchoSpacing']*1000,'.15f')
    
    # Some options that may become user-specified in the future, but use standard HCP values for now
    # Cutoff for considering a volume "b0", generally b<10, but for 7T data they are b<70
    b0maxbval="100"                                   
    #Specified value is passed as the CombineDataFlag value for the eddy_postproc.sh script.
    CombineDataFlag="1"

    #If JAC resampling has been used in eddy, this value
    #determines what to do with the output file.
    #2 - include in the output all volumes uncombined (i.e.
    #    output file of eddy)
    #1 - include in the output and combine only volumes
    #    where both LR/RL (or AP/PA) pairs have been
    #    acquired
    #0 - As 1, but also include uncombined single volumes
    #Defaults to 1
    ExtraEddyArgs=""

    #new flag to force use of non-gpu version of eddy
    EddyNonGpuArg = True

    config = context.config
    params = OrderedDict()
    params['path'] = context.work_dir
    params['subject'] = config['Subject']
    params['dwiname'] = config['DWIName']
    params['posData'] = '@'.join(posData)
    params['negData'] = '@'.join(negData)
    params['PEdir'] = PEdir
    params['echospacing'] = EffectiveEchoSpacing
    params['gdcoeffs'] = GradientDistortionCoeffs
    params['dof'] = config['AnatomyRegDOF']
    params['b0maxbval'] = b0maxbval
    params['combine-data-flag'] = CombineDataFlag
    params['extra-eddy-arg'] = ExtraEddyArgs
    params['eddy-non-gpu'] = EddyNonGpuArg
  
    params['printcom'] = ' '

def validate(context):
    environ = context.gear_dict['environ']
    config = context.config
    inputs = context._invocation['inputs']
    if  ('DWIPositiveData' in inputs.keys()) and \
        ('DWINegativeData' in inputs.keys()):
        info_pos = inputs["DWIPositiveData"].object.info
        info_neg = inputs["DWINegativeData"].object.info
        if  ('PhaseEncodingDirection' in info_pos.keys()) and \
            ('PhaseEncodingDirection' in info_neg.keys()):
            pedir_pos = inputs["DWIPositiveData"].object.info.PhaseEncodingDirection
            pedir_neg = inputs["DWINegativeData"].object.info.PhaseEncodingDirection
            pedir_pos = tr("ijk", "xyz", pedir_pos)
            pedir_neg = tr("ijk", "xyz", pedir_neg)
            if pedir_pos == pedir_neg:
                raise Exception(
                    "DWIPositive and DWINegative must have " + \
                    "opposite phase-encoding directions."
                )
            elif not (
                ((pedir_pos, pedir_neg) == ("x-", "x")) or \
                ((pedir_pos, pedir_neg) == ("x", "x-")) or \
                ((pedir_pos, pedir_neg) == ("y-", "y")) or \
                ((pedir_pos, pedir_neg) == ("y", "y-")) \
            ):
                raise Exception(
                    "DWIPositive and DWINegative have unrecognized " + \
                    "phase-encoding directions"
                )
        else:
            raise Exception(
                "DWIPositive or DWINegative input data is missing " + \
                "PhaseEncodingDirection metadata!"
            )
    else:
        raise Exception(
            'DWIPositive or DWINegative input data is missing!'
        )
    
    # Loop through the individual Diffusion files
    for i in range(1,11):
        # i=1 is a special case here 
        # the list of Diffusion files follows the format of 
        # DWIPositiveData, DWIPositiveData2, ...3, ....
        if i==1:
            j=''
        else:
            j=i
        # We only add to posData and negData if both are present
        # If only one is present, warn them in validate()
        if  ('DWIPositiveData{}'.format(j) in inputs.keys()) and \
            ('DWINegativeData{}'.format(j) in inputs.keys()):
            # Grab the Phase Encoding
            info_pos = inputs['DWIPositiveData{}'.format(j)].object.info
            info_neg = inputs['DWINegativeData{}'.format(j)].object.info
            if  ('PhaseEncodingDirection' in info_pos.keys()) and \
                ('PhaseEncodingDirection' in info_neg.keys()):
                PE_pos = tr("ijk", "xyz", info_pos['PhaseEncodingDirection'])
                PE_neg = tr("ijk", "xyz", info_neg['PhaseEncodingDirection'])
            else:
                raise Exception(
                    'DWIPositiveData{} or DWINegativeData{} '.format(j,j) + \
                    'is missing "PhaseEncodingDirection!'
                )

            # Grab each of the pos/neg bvec/bval files or make them None
            if 'DWIPositiveBvec{}'.format(j) not in inputs.keys():
                raise Exception(
                    'DWIPositiveBvec{} is missing! Please include'.format(j) + \
                    ' as an input before proceeding.'
                )

            if 'DWINegativeBvec{}'.format(j) not in inputs.keys():
                raise Exception(
                    'DWINegativeBvec{} is missing! Please include'.format(j) + \
                    ' as an input before proceeding.'
                )

            if 'DWIPositiveBval{}'.format(j) not in inputs.keys():
                raise Exception(
                    'DWIPositiveBval{} is missing! Please include'.format(j) + \
                    ' as an input before proceeding.'
                )

            if 'DWINegativeBval{}'.format(j) not in inputs.keys():
                raise Exception(
                    'DWINegativeBval{} is missing! Please include'.format(j) + \
                    ' as an input before proceeding.'
                )

            if PE_pos == PE_neg:
                raise Exception(
                    'DWIPositiveData{} and DWINegativeData{} have '.format(j,j) + \
                    'the same PhaseEncodingDirection ({})!'.format(PE_pos)
                )
            elif not (
                ((pedir_pos,pedir_neg) == (PE_pos,PE_neg)) or \
                ((pedir_pos,pedir_neg) == (PE_neg,PE_pos))
            ):
                raise Exception(
                    'DWI input pair #${} phase-encoding directions '.format(j) + \
                    '({},{}) do not match primary '.format(PE_pos,PE_neg) + \
                    'pair ({},{}). Exiting!'.format(pedir_pos,pedir_neg)
                )

        # Warn of the Exclusive OR (XOR) case
        elif ('DWIPositiveData{}'.format(j) in inputs.keys()) ^ \
            ('DWINegativeData{}'.format(j) in inputs.keys()):
            log.warning(
                'Only one of DWIPositiveData{} or '.format(j) + \
                'DWINegativeData{} '.format(j) + \
                'was selected. Thus none of their related data is included ' + \
                'in this analysis.'
            )
    # if 'DWIPositiveData' in inputs.keys():
    #     info = inputs['DWIPositiveData']['object']['info']
    #     if 'EffectiveEchoSpacing' not in info.keys():
    #         raise Exception(
    #             '"EffectiveEchoSpacing" iis not found in DWIPositiveData. ' + \
    #             'This is required to continue! Exiting.'
    #         )

def execute(context):
    pass