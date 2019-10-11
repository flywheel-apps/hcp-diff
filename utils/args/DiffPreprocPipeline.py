from collections import OrderedDict
import os, os.path as op

from .common import build_command_list, exec_command
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
    config = context.config
    params = OrderedDict()
    params['path'] = context.work_dir
    params['subject'] = config['Subject']
    params['dwiname'] = config['DWIName']
    
    params['printcom'] = ' '
    pass

def validate(context):
    pass

def execute(context):
    pass