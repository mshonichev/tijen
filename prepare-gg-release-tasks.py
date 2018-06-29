import os

from optparse import OptionParser

parser = OptionParser()
parser.add_option("--var_dir", action='store', default=None)
parser.add_option("--res_dir", action='store', default=None)
options, args = parser.parse_args()

# Make var_dir
if options.var_dir is None:
    var_dir = path.dirname(path.realpath(__file__)) + '/var'
else:
    var_dir = options.var_dir

os.makedirs(var_dir, exists_ok=True)

from util import versioned_yaml

ignite_version = os.environ.get('IGNITE_VERSION', '')

assert ignite_version != '', "IGNITE_VERSION environment variable not set"

assert options.res_dir is not None, "use --res_dir option to select resources for jobs"

res = versioned_yaml(ignite_version, '*.yaml', options.res_dir)

print(repr(res))
