import os, os.path as op
import shutil
import subprocess as sp
import re


def copy_diffusion_files(context,inputnii,inputbvec,inputbval,outputbase):
    os.makedirs(op.dirname(outputbase), exist_ok=True)
    environ = context.gear_dict['environ']
    FSLDIR = environ['FSLDIR']
    command = [op.join(FSLDIR,'bin','imcp')]
    command.extend([inputnii,outputbase])
    exec_command(context, command)

    shutil.copy(inputbvec, outputbase + '.bvec')
    shutil.copy(inputbval, outputbase + '.bval')

    command = ['imglob', '-extension', '"' + outputbase + '"']
    result = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE,
                        universal_newlines=True, env=environ)

    stdout, stderr = result.communicate()
    
    return stdout.split()

def build_command_list(command, ParamList, include_keys=True):
    """
    command is a list of prepared commands
    ParamList is a dictionary of key:value pairs to be put into the command 
     list as such ("-k value" or "--key=value")
    include_keys indicates whether to include the key-names with the command (True)
    """
    for key in ParamList.keys():
        # Single character command-line parameters are preceded by a single '-'
        if len(key) == 1:
            if include_keys:
                command.append('-' + key)
            if len(str(ParamList[key]))!=0:
                command.append(str(ParamList[key]))
        # Multi-Character command-line parameters are preceded by a double '--'
        else:
            # If Param is boolean and true include, else exclude
            if type(ParamList[key]) == bool:
                if ParamList[key] and include_keys:
                    command.append('--' + key)
            else:
                # If Param not boolean, but without value include without value
                # (e.g. '--key'), else include value (e.g. '--key=value')
                item = ""
                if include_keys:
                    item='--' + key
                if len(str(ParamList[key])) > 0:
                    if include_keys:
                        item = item + "="
                    item = item + str(ParamList[key])
                command.append(item)
    return command

def exec_command(context,command,shell=False,stdout_msg=None):
    environ = context.gear_dict['environ']
    context.log.info('Executing command: \n' + ' '.join(command)+'\n\n')
    if not context.gear_dict['dry-run']:
        # The 'shell' parameter is needed for bash output redirects 
        # (e.g. >,>>,&>)
        if shell:
            command = ' '.join(command)
        result = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE,
                        universal_newlines=True, env=environ, shell=shell)

        stdout, stderr = result.communicate()
        context.log.info('Command return code: {}'.format(result.returncode))

        if stdout_msg==None:
            context.log.info(stdout)
        else:
            context.log.info(stdout_msg)

        if result.returncode != 0:
            context.log.error('The command:\n ' +
                              ' '.join(command) +
                              '\nfailed.')
            raise Exception(stderr)