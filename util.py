
def version_num(version_text):
    """
    Convert text representation of version to number by format X.Y.Z to X0Y0Z
    For instance:
     1.2.3 -> 1020300
     1.2.3-p5 -> 1020305
    :param version_text:
    :return:
    """
    version_text = sub(r'\.(b|t)\d+$', '', version_text)
    version_text = sub(r'-QA[A-Z]+\d+$', '', version_text)
    version_text = sub(r'\.final', '', version_text)
    version_text = sub(r'-p', '.', version_text)
    ver_parts = version_text.split('.')
    if len(ver_parts) < 2:
        ver_parts.append('0')
    if len(ver_parts) < 3:
        ver_parts.append('0')
    if len(ver_parts) < 4:
        ver_parts.append('0')
    return 1000000*int(ver_parts[0]) + 10000*int(ver_parts[1]) + 100*int(ver_parts[2]) + int(ver_parts[3])


def versioned_files(*args):
    """
    Build a set of files matching for range of ignite version from major to given.
    E.g. for given ignite version '2.3.1', all existing files from '2.0.0' to '2.3.1' will be returned.
    :param args:
        args[0] - ignite version string, e.g. '2.3.1'
        args[1] - file mask, 'my.*.file', or a list of masks
        args[2] - base directory to search for files in
    :return: dictionary of files, indexed by ignite version number, e.g.
          { 2000000: '/my.2.file',
            2030000: '/my.2.3.file' }
    """
    high_ver_num = version_num(args[0])         # convert version string '2.3.1' to number, e.g.  2030100
    low_ver_num = 1000000*int(args[0][0:1])     # get major version number, e.g. for '2.3.1'      2000000
    if isinstance(args[1], list):
        glob_mask = args[1]
    elif isinstance(args[1], str):
        glob_mask = [args[1]]
    directories = []
    if isinstance(args[2], list):
        directories = args[2]
    elif isinstance(args[2], str):
        directories.append(args[2])
    files = {}
    for directory in directories:
        for file_glob in glob_mask:
            for file in glob("%s/%s" % (directory, file_glob)):
                m = search('[a-z]+\.([0-9\.]+)\.[a-z]+', file)
                if m:
                    cur_ver_num = version_num(m.group(1))
                    if high_ver_num >= cur_ver_num >= low_ver_num:
                        if cur_ver_num in files:
                            if isinstance(files[cur_ver_num], list):
                                files[cur_ver_num].append(file)
                            else:
                                files[cur_ver_num] = [files[cur_ver_num], file]
                        else:
                            files[cur_ver_num] = file
    return files
def versioned_yaml(*args, **kwargs):
    """
    Make the dictionary by merging YAML dictionaries from oldest ot newest version
    :param args:
        args[0] - ignite version string, e.g. '2.3.1'
        args[1] - YAML file glob mask, e.g. 'conf.*.yaml', or a list of masks
        args[2] - base directory to search for YAML files in
    :return:
    """
    yaml_files = versioned_files(args[0], args[1], args[2])
    data = {}
    for yaml_key in sorted(yaml_files.keys()):
        yaml_file = yaml_files[yaml_key]
        if type(yaml_file) == type([]):
            yaml_file_list = yaml_file
        else:
            yaml_file_list = [yaml_file]
        for yaml_file in yaml_file_list:
            with open(yaml_file) as r:
                try:
                    cur = yaml.load(r)
                    if len(data) == 0:
                        data = dict(cur)
                    else:
                        for key in cur.keys():
                            if data.get(key) is None:
                                if not (isinstance(cur[key], dict) and
                                                cur[key].get('_action') is not None and
                                                cur[key]['_action'] == 'delete'):
                                    data[key] = cur[key]
                            else:
                                if isinstance(cur[key], dict):
                                    if cur[key].get('_action') is not None:
                                        if cur[key]['_action'] == 'delete':
                                            del data[key]
                                    else:
                                        for subkey in cur[key]:
                                            data[key][subkey] = cur[key][subkey]
                                elif isinstance(cur[key], list):
                                    data[key] = cur[key]
                except ParserError as e:
                    print('versioned_yaml(\'%s\',%s,%s) had found ParserError loading file \'%s\'\n%s' % (
                        args[0], args[1], args[2], yaml_file, str(e)))

                except TypeError as e:
                    print('versioned_yaml(\'%s\',%s,%s) had found TypeError loading file \'%s\'\n%s' % (
                        args[0], args[1], args[2], yaml_file, str(e)))
                    raise e
    # Set default options
    if data.get('_default'):
        default_options = data['_default'].copy()
        for key in data.keys():
            for default_key in default_options.keys():
                if data[key].get(default_key) is None:
                    data[key][default_key] = default_options[default_key].copy()
        del data['_default']
    return data


def version_dir(*args):
    """
    Search through a group of directories specified by list of base paths and prefix.
    Return (configuration) directory best matching to specified ignite version.
    :param args:
        args[0] - ignite version, string, e.g. '2.3.1'
        args[1] - directory prefix, string, e.g. 'attr'
        args[2] - directory paths, list, e.g. ['base', 'extend']
    :return: None, if did not found any match, otherwise, one of ['base/attr.2', 'base/attr.2.3', ... ]
    """
    high_ver_num = version_num(args[0])         # convert version string '2.3.1' to version num.       e.g. 2030100
    low_ver_num = 1000000*int(args[0][0:1])     # convert major part of version string to version num. e.g. 2000000
    dir_prefix = args[1]
    dir_paths = args[2]
    latest_matched_version = low_ver_num
    latest_matched_path = None
    for dir_path in dir_paths:
        for subdir in listdir(dir_path):
            if subdir.startswith(dir_prefix):
                m = search('\.([0-9\.]+)$', subdir)
                if m:
                    cur_ver_num = version_num(m.group(1))       # convert version
                    if high_ver_num >= cur_ver_num >= low_ver_num:
                        if latest_matched_version <= cur_ver_num:
                            latest_matched_version = cur_ver_num
                            latest_matched_path = "%s/%s" % (dir_path, subdir)
    return latest_matched_path

