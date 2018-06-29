import os
from util import versioned_yaml, load_yaml, save_yaml, camelcase
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--var-dir", action='store', default=None)
    parser.add_option("--res-dir", action='store', default=None)
    options, args = parser.parse_args()

    # Make var_dir
    if options.var_dir is None:
        var_dir = os.path.dirname(os.path.realpath(__file__)) + '/var'
    else:
        var_dir = options.var_dir

    os.makedirs(var_dir, exist_ok=True)

    ignite_version = os.environ.get('IGNITE_VERSION', '')

    assert ignite_version != '', "IGNITE_VERSION environment variable not set"

    gridgain_version = os.environ.get('GRIDGAIN_VERSION', '')

    # don't assert on GRIDGAIN_VERSION not set, because it can be only AI release
    # assert gridgain_version != '', "GRIDGAIN_VERSION environment variable not set"

    test_plan = os.environ.get('TEST_PLAN', 'release').lower()
    # 'Debug' only differs from 'Release' but NOT uploading results to QA FTP
    root_folder_name = test_plan
    debug = False
    if test_plan == 'debug':
        debug = True
        test_plan = 'release'

    assert options.res_dir is not None, "use --res_dir option to select resources for jobs"

    base_template = os.path.join(os.path.dirname(__file__), 'res', 'template.yaml')
    print("*** Loading %s ***" % base_template)

    # first load 'base' template
    template = load_yaml(base_template)

    # then extend it with template specific to release type (ai/gg-ult-fab/...)
    res_template = os.path.abspath(os.path.join(options.res_dir, 'template.yaml'))
    print("*** Loading %s ***" % res_template)
    template.extend(load_yaml(res_template))

    print("*** Loading jobs specifications from %s ***" % os.path.abspath(options.res_dir))
    jobs = versioned_yaml(ignite_version, test_plan + '-jobs.*.yaml', os.path.abspath(options.res_dir))

    for k, v in enumerate(template):
        if 'project' in template[k]:
            template[k]['project']['ignite_version'] = ignite_version
            template[k]['project']['gridgain_version'] = gridgain_version
            template[k]['project']['root_folder_name'] = root_folder_name
            template[k]['project']['root_folder_display_name'] = camelcase(root_folder_name)

            jobs_list = []
            # first collect all folder jobs
            for job_name, job in jobs.items():
                if 'job-folder' in job[0].keys():
                    jobs_list.extend(job)
            # then collect all other jobs
            for job_name, job in jobs.items():
                if 'job-folder' not in job[0].keys():
                    if debug:
                        if 'job-tiden' in job[0].keys():
                            job = {
                                'job-tiden-debug': job[0]['job-tiden'].copy()
                            }
                    jobs_list.extend(job)

            if len(jobs_list) > 0:
                template[k]['project']['jobs'] = jobs_list

            # there should be only one 'project' per release type
            break

    # ok, done preparing, please handle this file to `jenkins-jobs`
    file = os.path.join(var_dir, 'job-generator.yaml')
    save_yaml(file, template)
    print("*** Generated jobs to %s ***" % file)
