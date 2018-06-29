import os
from util import versioned_yaml, load_yaml, save_yaml, camelcase
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--var-dir", action='store', default=None)
    parser.add_option("--res-dir", action='store', default=None)
    parser.add_option("--root-folder", action='store', default='release')
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

    # assert gridgain_version != '', "GRIDGAIN_VERSION environment variable not set"

    assert options.res_dir is not None, "use --res_dir option to select resources for jobs"

    template = load_yaml(os.path.join(options.res_dir, 'template.yaml'))

    jobs = versioned_yaml(ignite_version, 'jobs.*.yaml', options.res_dir)

    for k, v in enumerate(template):
        if 'project' in template[k]:
            template[k]['project']['ignite_version'] = ignite_version
            template[k]['project']['gridgain_version'] = gridgain_version
            template[k]['project']['root_folder_name'] = options.root_folder
            template[k]['project']['root_folder_display_name'] = camelcase(options.root_folder)

            jobs_list = []
            for job_name, job in jobs.items():
                job['name'] = job_name
                jobs_list.append(job.copy())

            if len(jobs_list) > 0:
                template[k]['project']['jobs'] = jobs_list

            break

    save_yaml(os.path.join(var_dir, 'job-generator.yaml'), template)

