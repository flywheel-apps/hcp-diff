import os, os.path as op
import glob

def remove_intermediate_files(context):
    ##################Delete extraneous processing files#################
    config = context.config
    # Delete temporary input files (re-organized DWI inputs)
    # These files are not in ./work/{subject} so we don't care.
    try:
        shutil.rmtree(
            op.join(
                context.work_dir,
                'tmp_input'
            )
        )
    except:
        pass

    del_niftis = glob.glob(
        op.join(
            context.work_dir,
            config['Subject'],
            config['fMRIName'],
            'MotionMatrices',
            '*.nii.gz'
        )
    )

    try:
        for nifti in del_niftis:
            os.remove(nifti)
    except:
        pass

def configs_to_export(context):
    config = {}
    hcpdiff_config={'config': config}
    for key in [
        'RegName',
        'Subject',
        'DWIName'
    ]:
        if key in context.config.keys():
            config[key]=context.config[key]
    
    hcpdiff_config_filename = op.join(
            context.work_dir,context.config['Subject'],
            '{}_{}_hcpfunc_config.json'.format(
                context.config['Subject'],
                context.config['DWIName']
            )
    )

    return hcpdiff_config, hcpdiff_config_filename

def make_sym_link(src, dest):
    if src:
        os.symlink(src, dest)