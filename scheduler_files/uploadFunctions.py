#!/usr/bin/python
import psycopg2 as psg
import sys
import yaml
import subprocess
import json
import datetime
import os

configFileName=os.path.dirname(os.path.abspath(__file__)) + '/configuration.json'
configFile=open(configFileName,'r')
config=json.load(configFile)
configFile.close()

db=config['database']
host=db['host']
dbuser=db['username']
passwd=db['password']
dbname=db['database']

def cwlReadFile(filename):
    f=open(filename,'r')
    try:
        content=yaml.load(f,Loader=yaml.FullLoader)
    except Exception as exp:
        print(str(exp))
        exit(26)
    f.close()

    return content
    #Database configuration

    #Read yaml file content

def deleteSavedSoftware(name,version):
    executable=os.path.dirname(os.path.abspath(__file__)) + '/imageRemover.py'
    subprocess.call([executable,name,version])


def cwlReturnDockerImage(content):
    if 'hints' not in content and 'requirements' not in content:
        return ''
    hints=[]
    requirements=[]
    if 'hints' in content:
        hints=content['hints']
    # print(hints)
    if 'requirements' in content:
        requirements=content['requirements']
    hintDockerImage=''
    reqDockerImage=''
    #if hints is a list
    if len(hints)>=1:
        appearances=0
        for hint in hints:
            # print(hint)
            if 'DockerRequirement' in hint:
                docker=hint['DockerRequirement']
                appearances+=1
            elif 'class' in hint:
                if  hint['class']=='DockerRequirement':
                    if 'dockerPull' in hint:
                        docker=hint
                    appearances+=1
        #if the user declared no images or declared more than one image
        if appearances==0:
            return ''
        elif appearances>1:
            exit(22)
        else:
            if 'dockerPull' in docker:
                hintDockerImage=docker['dockerPull']
    # #if hints is a list and a DockerRequirement exists
    # else:
    #     if 'DockerRequirement' in hints:
    #         docker=hints['DockerRequirement']
    #         if 'dockerPull' in docker:
    #             hintDockerImage=docker['dockerPull']
    #if requirements is a list
    if len(requirements)>=1:
        appearances=0
        for req in requirements:
            # print(req)
            if 'DockerRequirement' in req:
                docker=req['DockerRequirement']
                appearances+=1
            elif 'class' in req:
                # print (req)
                if  req['class']=='DockerRequirement':
                    if 'dockerPull' in req:
                        docker=req['dockerPull']
                    else:
                        docker=req
                    appearances+=1
        if appearances==0:
            return ''
        elif appearances>1:
            exit(22)
        else:
            if 'dockerPull' in docker:
                reqDockerImage=docker['dockerPull']
    else:
        if 'DockerRequirement' in requirements:
            docker=req['DockerRequirement']
            if 'dockerPull' in docker:
                reqDockerImage=docker['dockerPull']

    if reqDockerImage=='' and hintDockerImage=='':
        return ''
    elif reqDockerImage!='' and hintDockerImage=='':
        return reqDockerImage
    elif reqDockerImage=='' and hintDockerImage!='':
        return hintDockerImage
    else:
        if reqDockerImage==hintDockerImage:
            return reqDockerImage
        else:
            exit(23)

def inputStore(softName,softVersion, inputs):
    types=set(['string', 'int', 'long', 'float', 'double', 'null', 'File', 'Directory', 'Any','boolean'])

    #open db connection and get image id
    conn=psg.connect(host=host, user=dbuser, password=passwd, dbname=dbname)
    cur=conn.cursor()

    query="SELECT id FROM software WHERE name='" + softName + "' AND version='" + softVersion + "'"
    cur.execute(query)
    result=cur.fetchall()
    softId=str(result[0][0])

    #save script in database and get its id
    # print(inputs)
    if len(inputs)==0:
        exit(30)

    #create queries for input insertion
    query='INSERT INTO software_inputs(name, position, softwareid, field_type, prefix, separate, optional, default_value, is_array, array_separator, nested_array_binding) VALUES '

    bindingFlag=False
    positionFlag=False
    separateInner=False
    prefixInner=False


    for inpt in inputs:
        is_array='f'
        array_separator=''
        nested_array_binding='f'
        prefix=''
        separate='f'
        if 'type' not in inputs[inpt]:
            #stop execution and return because this is serious
            deleteSavedSoftware(softName,softVersion)
            return 34
        fieldType=inputs[inpt]['type']
        #field type is array
        if isinstance(fieldType,dict):
            if fieldType['type']!='array':
                deleteSavedSoftware(softName,softVersion)
                return 36
            is_array='t'
            if 'inputBinding' in fieldType:
                nested_array_binding='t'
                innerBinding=fieldType['inputBinding']
                if 'separate' in binding:
                    separateInner=True
                    if innerBinding['separate']==True:
                        separate='t'
                if 'prefix' in binding:
                    prefixInner=True
                    prefix=innerBinding['prefix']
            if 'items' not in fieldType:
                deleteSavedSoftware(softName,softVersion)
                return 37

            fieldType=fieldType['items']

        else:
            fieldType=inputs[inpt]['type'].strip()

        
        if 'inputBinding' not in inputs[inpt]:
                bindingFlag=True
                continue
                #exit(32)

               
        outerBinding=inputs[inpt]['inputBinding']
        # Get position, separate and prefix from inputBinding.
        # If it does not exist, ignore input
        if 'position' not in outerBinding:
            positionFlat=True
            continue
        position=outerBinding['position']

        if ('separate' in outerBinding) and (separateInner==False):
            if outerBinding['separate']=='false':
                separate='f'
            else:
                separate='t'

        if ('prefix' in outerBinding) and (prefixInner==False):
            prefix=outerBinding['prefix'] 
        if ('itemSeparator' in outerBinding):
            array_separator=outerBinding['itemSeparator']     
        
        # print(separate)

        optional='f'
        if fieldType[-1]=='?':
            optional='t'
            fieldType=fieldType[:-1]

        if '[]' in fieldType:
            is_array='t'
            fieldType=fieldType[:-2]
        
        if fieldType not in types:
            #stop execution and return because this is serious
            deleteSavedSoftware(softName,softVersion)
            print(fieldType)
            return 35
            
            
            #get default value
        defaultValue=''
        if (fieldType!='File') and (fieldType!='Directory') and (fieldType!='null'):
            if 'default' in inputs[inpt]:
                defaultValue=str(inputs[inpt]['default'])

        name=quoteEnclose(inpt)
        fieldType=quoteEnclose(fieldType)
        prefix=quoteEnclose(prefix)
        defaultValue=quoteEnclose(defaultValue)
        optional=quoteEnclose(optional)
        separate=quoteEnclose(separate)
        is_array=quoteEnclose(is_array)
        array_separator=quoteEnclose(array_separator)
        nested_array_binding=quoteEnclose(nested_array_binding)

        query+='(' + name + ',' + str(position) + ',' + str(softId) + ',' + fieldType + ',' + prefix + ',' + separate + ',' + optional + ',' + defaultValue + ',' + is_array+ ',' + array_separator + ',' + nested_array_binding + '),'

    query=query[:-1]
    # print(query)
    cur.execute(query)
    conn.commit()

    conn.close()

    if bindingFlag:
        return 32
    if positionFlag:
        return 33

    return 0

def imageStoreAndClassify(name,version,image,script,user,visibility,
                workingDir,imountPoint,omountPoint, description,cwlPath,biotools,doiFile,mpi,original,docker_or_local,covid19):
    
    softFull=name+ '-' + version
    name=quoteEnclose(name)
    version=quoteEnclose(version)
    image=quoteEnclose(image)
    script=quoteEnclose(script)
    user=quoteEnclose(user)
    visibility=quoteEnclose(visibility)
    workingDir=quoteEnclose(workingDir)
    imountPoint=quoteEnclose(imountPoint)
    omountPoint=quoteEnclose(omountPoint)
    description=quoteEnclose(description)
    cwlPath=quoteEnclose(cwlPath)
    biotools=quoteEnclose(biotools)
    mpi=quoteEnclose(mpi)
    original=quoteEnclose(original)
    docker_or_local=quoteEnclose(docker_or_local)
    covid19=quoteEnclose(covid19)

    if doiFile!='':
        f=open(doiFile)
        dois=f.readline().strip()
        f.close()
    else:
        dois=''
    dois=quoteEnclose(dois)

    date="NOW()"

    values=[name,version,image,script,user, date, visibility, workingDir, imountPoint, 
                omountPoint, description, cwlPath,biotools,dois,mpi,original,docker_or_local,covid19]
    
    sql1='INSERT INTO software_upload (name,version, image,script,uploaded_by, date, visibility, workingdir, imountpoint, omountpoint,\
    description, cwl_path,biotools,dois,mpi,original_image,docker_or_local,covid19) '
    sql1+='VALUES (' + ','.join(values) + ')'

    # print(sql1);

    
    ## classify software

    # ontologyFolder="/data/www/schema/scheduler_files/ontology/";
    # command=[ontologyFolder + 'initialClassify.py', softFull, '100', '100','64', '0', '0']
    # # print(' '.join(command))
    # # exit(0)
    # try:
    #     out=subprocess.check_output(command,stderr=subprocess.STDOUT)
    # except subprocess.CalledProcessError as exc:
    #     print(exc.output)
    #     exit(24)

    values=[name,version,image,script,user, visibility, workingDir, imountPoint, omountPoint,description,cwlPath,biotools,
                    dois,mpi,original,docker_or_local,covid19]
    sql2='INSERT INTO software (name,version,image,script,uploaded_by,\
            visibility, workingdir, imountpoint, omountpoint, description,\
            cwl_path,biotools,dois,mpi,original_image,docker_or_local,covid19) '
    sql2+='VALUES (' + ','.join(values) + ')'
    
    # print()
    # print(sql2)
    conn=psg.connect(host=host, user=dbuser, password=passwd, dbname=dbname)
    cur=conn.cursor()
    cur.execute(sql1)
    cur.execute(sql2)
    conn.commit()
    conn.close()


def quoteEnclose(string):
    return "'" + string + "'"
