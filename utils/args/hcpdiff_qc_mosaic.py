"""
Builds, validates, and excecutes parameters for the HCP helper script 
/tmp/scripts/hcpdiff_qc_mosaic.sh
part of the hcp-diff gear
"""

from collections import OrderedDict
import os, os.path as op

from .common import build_command_list, exec_command

# qc_scene_root="${StudyFolder}/${Subject}"

# qc_outputdir="${StudyFolder}"
# mkdir -p ${qc_outputdir}

# qc_image_root="${qc_outputdir}/${Subject}_${DWIName}.hcpdiff_QC."

# set -x
# ${RUN_QC} ${SCRIPT_DIR}/hcpdiff_qc_mosaic.sh \
#   ${qc_scene_root} \
#   ${DWIName} \
#   ${qc_image_root} > ${LogFileDirFull}/diffusionqc.log

# qc_exit_staus=$?

# set +x
def build(context):
    config = context.config
    params = OrderedDict()

    params['qc_scene_root'] = op.join(context.work_dir, config['Subject'])
    params['DWIName'] = config['DWIName']
    params['qc_image_root'] = op.join(
        context.work_dir,
        config['Subject'] + '_' + config['DWIName'] + '.hcpdiff_QC.'
    )
    context.gear_dict['QC-Params'] = params

def validate(context):
    pass

def execute(context):
    SCRIPT_DIR = context.gear_dict['SCRIPT_DIR']
    command = [op.join(SCRIPT_DIR,'hcpdiff_qc_mosaic.sh')]

    command = build_command_list(
        command, context.gear_dict['QC-Params'], include_keys = False
    )

    command.append('>')
    command.append(op.join(context.work_dir, 'logs', 'diffusionqc.log'))

    stdout_msg = 'Pipeline logs (stdout, stderr) will be available ' + \
                 'in the file "pipeline_logs.zip" upon completion.'

    context.log.info('Diffusion QC Image Generation command: \n')
    exec_command(context, command, shell = True, stdout_msg = stdout_msg)