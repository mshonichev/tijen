def ignite_version = readFileFromWorkspace('ignite_version.txt')

folder(ignite_version) {
    displayName('Release ' + ignite_version)
    description('Distributed tests for release ' + ignite_version)

    job('prepare') {
        parameters {
            stringParam('IGNITE_VERSION', ignite_version, 'Ignite version')
        }
        steps {
             shell('set')
        }
    }
}