import os
from util import versioned_yaml, load_yaml, save_yaml, camelcase
from optparse import OptionParser
from copy import deepcopy
import re

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

    tiden_job = None
    for k, v in enumerate(template):
        if 'job-template' in template[k]:
            if 'id' in template[k]['job-template']:
                if 'job-tiden' == template[k]['job-template']['id']:
                    tiden_job = deepcopy(template[k])
                    break

    if tiden_job:
        tiden_debug_job = deepcopy(tiden_job)
        tiden_debug_job['job-template']['id'] = 'job-tiden-debug'
        for k, v in enumerate(tiden_debug_job['job-template']['publishers']):
            if 'ftp' in tiden_debug_job['job-template']['publishers'][k]:
                if 'Publish_to_QA_FTP' == tiden_debug_job['job-template']['publishers'][k]['ftp']['site']:
                    del tiden_debug_job['job-template']['publishers'][k]

                    break

        template.append(tiden_debug_job)

    naive_build_all_job = None
    for k, v in enumerate(template):
        if 'job-template' in template[k]:
            if 'id' in template[k]['job-template']:
                if 'job-buildall-naive' == template[k]['job-template']['id']:
                    naive_build_all_job = template[k]
                    break

    print("*** Loading jobs specifications from %s ***" % os.path.abspath(options.res_dir))
    jobs = versioned_yaml(ignite_version, test_plan + '-jobs.*.yaml', os.path.abspath(options.res_dir))

    job_folder = '{root_folder_name}/{edition_name}/{ignite_version}'
    edition_name = ''
    for k, v in enumerate(template):
        if 'project' in template[k]:
            template[k]['project']['ignite_version'] = ignite_version
            template[k]['project']['gridgain_version'] = gridgain_version
            template[k]['project']['root_folder_name'] = root_folder_name
            edition_name = template[k]['project']['edition_name']
            template[k]['project']['root_folder_display_name'] = camelcase(root_folder_name)

            jobs_list = []
            # first collect all folder jobs
            for job_name, job in jobs.items():
                job_type = list(job[0].keys())[0]
                if 'job-folder' == job_type:
                    jobs_list.extend(job)

            # then collect all other jobs but for buildall
            for job_name, job in jobs.items():
                job_type = list(job[0].keys())[0]
                if 'job-folder' != job_type and 'buildall' not in job_type:
                    if 'job-tiden' == job_type:
                        job[0][job_type]['job_folder'] = job_folder

                        if debug:
                            job = [{
                                'job-tiden-debug': deepcopy(job[0][job_type])
                            }]

                    jobs_list.extend(job)

            # generate naive buildall job
            if naive_build_all_job is not None:
                for job_name, job in jobs.items():
                    job_type = list(job[0].keys())[0]
                    if 'job-buildall-naive' == job_type:
                        phase_regex = '.*'
                        if 'phase_regex' in job[0][job_type]:
                            phase_regex = job[0][job_type]['phase_regex']

                        step_names = []
                        for job_name, job in jobs.items():
                            job_type = list(job[0].keys())[0]
                            if job_type != 'job-folder' and 'buildall' not in job_type:
                                job_short_name = None
                                if 'job-tiden' in job_type:
                                    suite_name = job[0][job_type]['suite_name']
                                    job_short_name = 'tiden-' + suite_name
                                elif 'job-ddtest' in job_type:
                                    suite_name = job[0][job_type]['suite_name']
                                    job_short_name = 'ddtest-' + suite_name
                                elif 'name' in job[0][job_type].keys():
                                    job_short_name = job[0][job_type]['name']
                                if job_short_name is not None:
                                    if re.match(phase_regex, job_short_name):
                                        step_names.append(
                                            '/'.join([root_folder_name, edition_name, ignite_version, job_short_name]))

                        # now update multijob template (ooops, it can be used only once per suite!)

                        # update job name to put it under folder
                        naive_build_all_job['job-template']['name'] = '/'.join(
                            [root_folder_name, edition_name, ignite_version,
                             naive_build_all_job['job-template']['name']])

                        # extract step template ...
                        build_all_phase = None
                        for phase in naive_build_all_job['job-template']['builders']:
                            if 'multijob' in phase:
                                if 'id' in phase['multijob'] and phase['multijob']['id'] == 'tests':
                                    build_all_phase = phase['multijob']
                                    break
                        if build_all_phase is not None:
                            step_template = deepcopy(build_all_phase['projects'][0])
                            # ... and remove all current steps ...
                            build_all_phase['projects'] = []

                            # ... in order to add only required steps
                            for step_name in step_names:
                                step = deepcopy(step_template)
                                step['name'] = step_name
                                build_all_phase['projects'].append(step)

                            job = [{
                                'job-buildall-naive': {}
                            }]
                            jobs_list.extend(job)
                            break

            if len(jobs_list) > 0:
                template[k]['project']['jobs'] = jobs_list

            # there should be only one 'project' per release type
            break

    # ok, done preparing, please handle this file to `jenkins-jobs`
    file = os.path.join(var_dir, 'job-generator.yaml')
    save_yaml(file, template)
    print("*** Generated jobs to %s ***" % file)
